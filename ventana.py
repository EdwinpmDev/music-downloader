import sys
from PyQt6.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox,QWidget

# Importe de funciones desde el main
from main import *


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.startUI()

    # Interface

    def startUI(self):
        self.setGeometry(100, 100, 400, 600) # x,y,ancho,largo
        self.setWindowTitle("MusicDownloader")
        self.interface()
        self.show()

    def interface(self):
        self.input_link = QLineEdit(self)
        self.input_link.setPlaceholderText("Paste link here")
        self.input_link.move(50, 100)
        self.input_link.resize(100, 150) # Width and Height

        self.format_selector = QComboBox(self)
        self.format_selector.addItems(['m4a', 'aac', 'mp3', 'ogg', 'opus', 'webm'])
        self.format_selector.move(200, 200)

        self.button_download = QPushButton("Descargar", self)
        self.button_download.move(150, 150)
        self.button_download.clicked.connect(self.download_audio)

    # Logic
    def download_audio(self):
        # Collect data
        enlace = self.input_link.text()
        selected_format = self.format_selector.currentText()
        # Send data to backend in "descarga_audio"
        urls_audio = [enlace]
        descarga_audio(urls_audio, selected_format)

        print("Descargando: ", enlace)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    sys.exit(app.exec())