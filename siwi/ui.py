from PyQt6.QtWidgets import QLabel, QMainWindow
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from siwi.pipe import Pipe

class LabelWriter(QObject, Pipe[str, None]):
	text_ready = pyqtSignal(str)

	def receive(self, data):
		self.text_ready.emit(data.strip())

class MainWindow(QMainWindow):
	def __init__(self, label_writer: LabelWriter):
		super().__init__()

		self.setWindowTitle("Say It, Write It")
		self.setWindowFlags(Qt.WindowType.Window)
		self.setStyleSheet("""
			background-color: #000;
			padding: 16px;
		""")
		self.resize(800, 150)

		self._label = self._create_label()
		self.setCentralWidget(self._label)

		label_writer.text_ready.connect(self.set_text)

	def set_text(self, text):
		self._label.setText(text)

	def _create_label(self):
		label = QLabel("Welcome to Say It, Write It!")

		label.setWordWrap(True)
		label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
		label.setStyleSheet("""
			color: #fff;
			font-size: 24pt;
		""")

		return label