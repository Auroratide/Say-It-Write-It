from PyQt6.QtWidgets import QLabel, QMainWindow
from PyQt6.QtCore import QObject, pyqtSignal
from siwi.pipe import Pipe

class LabelWriter(QObject, Pipe[str, None]):
	text_ready = pyqtSignal(str)

	def receive(self, data):
		self.text_ready.emit(data)

class MainWindow(QMainWindow):
	def __init__(self, label_writer: LabelWriter):
		super().__init__()

		self.setWindowTitle("Say It, Write It")
		self.label = QLabel("Hell owrld ")

		self.setCentralWidget(self.label)

		label_writer.text_ready.connect(self.set_text)

	def set_text(self, text):
		self.label.setText(text)

