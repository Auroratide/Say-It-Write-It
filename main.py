from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
import sounddevice as sd
from faster_whisper import WhisperModel
import threading
import queue
import numpy as np

SAMPLE_RATE = 16000
CHUNK_SECONDS = 2
stt_model = WhisperModel("base", device="cpu")

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("Say It, Write It")
		label = QLabel("Hell owrld ")

		self.setCentralWidget(label)

audio = queue.Queue()

def read_audio(indata, frames, time, status):
	audio.put(indata.copy())

def process_audio():
	buffer = np.array([], dtype=np.float32)
	with sd.InputStream(channels=1, samplerate=SAMPLE_RATE, callback=read_audio):
		while True:
			chunk = audio.get()
			buffer = np.concatenate([buffer, chunk.flatten()])
			if len(buffer) > SAMPLE_RATE * CHUNK_SECONDS:
				segments, _ = stt_model.transcribe(buffer, vad_filter=True)
				text = " ".join(s.text for s in segments)
				print(text)
				buffer = np.array([], dtype=np.float32)

def main():
	print(sd.query_devices())

	app = QApplication([])

	window = MainWindow()
	window.show()

	thread = threading.Thread(target=process_audio, daemon=True)
	thread.start()

	app.exec()

if __name__ == "__main__":
	main()
