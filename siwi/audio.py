import threading
import queue
import torch
import sounddevice as sd
import numpy as np
from siwi.pipe import Pipe
from silero_vad import VADIterator
from faster_whisper import WhisperModel
from platformdirs import user_data_dir
from pathlib import Path

SAMPLE_RATE = 16000
BLOCKSIZE = 512
CHUNK_SECONDS = 1

def model_location(name: str) -> str:
	models_dir = Path(user_data_dir(appname="SayItWriteIt", appauthor=False))	
	return str(models_dir / name)

class AudioStream(Pipe[None, np.ndarray]):
	_audio = queue.Queue()

	def start(self):
		self._thread = threading.Thread(target=self._process_audio_queue, daemon=True)
		self._thread.start()

	def _process_audio_queue(self):
		with sd.InputStream(channels = 1, samplerate=SAMPLE_RATE, blocksize=BLOCKSIZE, callback=self._read_audio_into_queue):
			while True:
				audio = self._audio.get()
				self.send(audio)

	def _read_audio_into_queue(self, indata, frames, time, status):
		self._audio.put(indata.copy())

class VadBuffer(Pipe[np.ndarray, np.ndarray]):
	def __init__(self):
		super().__init__()
		torch.hub.set_dir(model_location("silero"))
		model, _ = torch.hub.load(repo_or_dir="snakers4/silero-vad", model="silero_vad", trust_repo=True)
		self._vad = VADIterator(model=model, sampling_rate=SAMPLE_RATE, min_silence_duration_ms=CHUNK_SECONDS * 1000)
		self._hot = False
		self._chunk_buffer = np.array([], dtype=np.float32)
		self._phrase_buffer = np.array([], dtype=np.float32)

	def receive(self, data):
		as_tensor = torch.from_numpy(data.flatten())
		speech_dict = self._vad(as_tensor, return_seconds=True)
		start_detected = speech_dict and speech_dict.get("start")
		end_detected = speech_dict and speech_dict.get("end")
		
		if start_detected:
			self._hot = True
		elif end_detected:
			self._hot = False

		if self._hot or end_detected:
			self._chunk_buffer = np.concatenate([self._chunk_buffer, data.flatten()])
			self._phrase_buffer = np.concatenate([self._phrase_buffer, data.flatten()])

			if end_detected or len(self._chunk_buffer) > SAMPLE_RATE * CHUNK_SECONDS:
				self._send_current_phrase()

	def _send_current_phrase(self):
		self.send(self._phrase_buffer)
		self._chunk_buffer = np.array([], dtype=np.float32)
		if not self._hot:
			self._phrase_buffer = np.array([], dtype=np.float32)

class Transcription(Pipe[np.ndarray, str]):
	def __init__(self):
		super().__init__()
		self._model = WhisperModel("base", device="cpu", download_root=model_location("whisper"))
	
	def receive(self, data):
		segments, _ = self._model.transcribe(data, condition_on_previous_text=False)
		text = " ".join(s.text for s in segments)
		self.send(text)