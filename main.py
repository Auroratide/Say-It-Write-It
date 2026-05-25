from PyQt6.QtWidgets import QApplication
import sounddevice as sd
from siwi.ui import MainWindow, LabelWriter
from siwi.audio import AudioStream, VadBuffer, Transcription

def main():
	print(sd.query_devices())

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
