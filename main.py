import sys
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QMessageBox, QComboBox, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit

from backend import *

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.startUI()

    # Interface
    def startUI(self):
        self.setGeometry(100, 100, 400, 600) # x,y,width, height
        self.setWindowTitle('MusicDownloader')
        self.interface()
        self.show()

    def interface(self):        
        self.input_link = QLineEdit(self)
        self.input_link.setPlaceholderText("Paste link here")

        self.button_download = QPushButton('Download', self)
        self.button_download.clicked.connect(self.download_media)

        self.media_selector = QComboBox(self)
        self.media_selector.addItems(['Audio','Video'])
        self.media_selector.currentTextChanged.connect(self.media_change)

        self.format_selector = QComboBox(self)

        self.media_change() 

        # Layout
        GeneralLayout = QVBoxLayout()
        h_layout1 = QHBoxLayout()
        h_layout2 = QHBoxLayout()
        h_layout1.addWidget(self.input_link)
        h_layout1.addWidget(self.button_download)
        h_layout2.addWidget(self.media_selector)
        h_layout2.addWidget(self.format_selector)
        GeneralLayout.addLayout(h_layout1)
        GeneralLayout.addLayout(h_layout2)
        self.setLayout(GeneralLayout)

    # Logic
    def media_change(self):
        self.format_selector.clear()
        self.selected_media = self.media_selector.currentText()

        if self.selected_media == "Audio":
            self.format_selector.addItems(['mp3', 'aac', 'opus', 'm4a', 'ogg', 'webm'])
        else:
            self.format_selector.addItems(['mp4', 'm4a', 'webm'])


    def download_media(self):
        # Collect data
        link = self.input_link.text()
        selected_format = self.format_selector.currentText()
        urls = [link]
        # Checks if there's a valid URL
        if link == '':
            print("Put a valid URL")
            return
        
        try:
        # Send data to backEnd
            download_any_media(urls, selected_format, self.selected_media)
            print("Downloading media:", link)
        except:
            print("Download error")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    sys.exit(app.exec())