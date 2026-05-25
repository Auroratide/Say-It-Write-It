from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtCore import QObject, pyqtSignal
import sounddevice as sd
from faster_whisper import WhisperModel
from silero_vad import VADIterator
import threading
import queue
import numpy as np
import torch

SAMPLE_RATE = 16000
BLOCKSIZE = 512
CHUNK_SECONDS = 1
stt_model = WhisperModel("base", device="cpu")
vad_model, _ = torch.hub.load(repo_or_dir="snakers4/silero-vad", model="silero_vad")
vad_iterator = VADIterator(model=vad_model, sampling_rate=SAMPLE_RATE, min_silence_duration_ms=CHUNK_SECONDS * 1000)

class Transcriber(QObject):
	audio = queue.Queue()
	text_ready = pyqtSignal(str)

	def read_audio(self, indata, frames, time, status):
		self.audio.put(indata.copy())

	def process_audio(self):
		buffer = np.array([], dtype=np.float32)
		phrase_buffer = np.array([], dtype=np.float32)
		with sd.InputStream(channels=1, samplerate=SAMPLE_RATE, blocksize=BLOCKSIZE, callback=self.read_audio):
			end_detected = False
			while True:
				chunk = self.audio.get()
				tensor = torch.from_numpy(chunk.flatten())
				speech_dict = vad_iterator(tensor, return_seconds=True)
				if speech_dict and speech_dict.get("end"):
					print("end detected")
					end_detected = True
				buffer = np.concatenate([buffer, chunk.flatten()])
				phrase_buffer = np.concatenate([phrase_buffer, chunk.flatten()])

				if end_detected or len(buffer) > SAMPLE_RATE * CHUNK_SECONDS:
					segments, _ = stt_model.transcribe(phrase_buffer, vad_filter=True, condition_on_previous_text=False)
					text = " ".join(s.text for s in segments)
					print(text)
					self.text_ready.emit(text)
					buffer = np.array([], dtype=np.float32)
					if end_detected:
						phrase_buffer = np.array([], dtype=np.float32)
						vad_iterator.reset_states()
						end_detected = False

class MainWindow(QMainWindow):
	transcriber = Transcriber()

	def __init__(self):
		super().__init__()

		self.setWindowTitle("Say It, Write It")
		self.label = QLabel("Hell owrld ")

		self.setCentralWidget(self.label)

		self.transcriber.text_ready.connect(self.on_text)

	def on_text(self, text):
		self.label.setText(text)

def main():
	print(sd.query_devices())

	app = QApplication([])

	window = MainWindow()
	window.show()

	thread = threading.Thread(target=window.transcriber.process_audio, daemon=True)
	thread.start()

	app.exec()

if __name__ == "__main__":
	main()
