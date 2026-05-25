from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("Say It, Write It")
		label = QLabel("Hell owrld ")

		self.setCentralWidget(label)

def main():
	app = QApplication([])

	window = MainWindow()
	window.show()

	app.exec()


if __name__ == "__main__":
	main()
