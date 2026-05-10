import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QMessageBox, QFileDialog,QComboBox, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt6.QtCore import QThread

from src.core.downloader import *

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

class DownloadThread(QThread):
    def __init__(self, urls, selected_format, selected_media, directory_selected):
        super().__init__()
        self.urls = urls
        self.selected_format = selected_format
        self.selected_media = selected_media
        self.directory_selected = directory_selected

    def run(self):
        try:
            # Send data to backEnd
            download_any_media(
                self.urls, 
                self.selected_format, 
                self.selected_media, 
                self.directory_selected)
            print("Downloading media...")
        except Exception as e:
            print(f"Download error: {e}")


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

        self.directory_selector = QPushButton('Select download directory', self)
        self.directory_selector.clicked.connect(self.choose_directory)

        self.directory_selected = ''
        self.read_directory()
        self.media_change() 

        # Layout
        GeneralLayout = QVBoxLayout()
        h_layout1 = QHBoxLayout()
        h_layout2 = QHBoxLayout()
        h_layout3 = QHBoxLayout()
        h_layout1.addWidget(self.input_link)
        h_layout1.addWidget(self.button_download)
        h_layout2.addWidget(self.media_selector)
        h_layout2.addWidget(self.format_selector)
        h_layout3.addWidget(self.directory_selector)
        GeneralLayout.addLayout(h_layout1)
        GeneralLayout.addLayout(h_layout2)
        GeneralLayout.addLayout(h_layout3)
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
            # Create thread
            self.download_thread = DownloadThread(
                urls=urls,
                selected_format=selected_format,
                selected_media=self.selected_media,
                directory_selected=self.directory_selected
            )

            # Start thread
            self.download_thread.start()
            print("Download started in the background")
        except Exception as e:
            print(f"Download error: {e}")


    def choose_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Choose carpet')
        if directory:
            print(f'Directoy choosen: {directory}')
            self.directory_selected = directory
            self.save_directory()



    def read_directory(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as archive:
                data = json.load(archive)
                path = data['last_directory']
            self.directory_selected = path
        else:
            self.directory_selected = ''


    def save_directory(self):
        dictionary = {"last_directory": self.directory_selected}
        with open('config.json', 'w') as archive:
            json.dump(dictionary, archive)
            print("Path saved")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    sys.exit(app.exec())