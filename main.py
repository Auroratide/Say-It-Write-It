from PyQt6.QtWidgets import QApplication
import sounddevice as sd
from siwi.ui import MainWindow, LabelWriter
from siwi.audio import AudioStream, VadBuffer, Transcription
import sys, os
from platformdirs import user_data_dir

if sys.stderr is None:
	log_path = os.path.join(user_data_dir("SayItWriteIt", appauthor=False), "log.txt")
	sys.stderr = open(log_path, "w")
if sys.stdout is None:
	sys.stdout = sys.stderr

def main():
	# print(sd.query_devices())

	app = QApplication([])

	label_writer = LabelWriter()
	window = MainWindow(label_writer)
	window.show()

	audio_stream = AudioStream()
	audio_stream.pipe(VadBuffer()).pipe(Transcription()).pipe(label_writer)
	audio_stream.start()

	app.exec()

if __name__ == "__main__":
	main()
