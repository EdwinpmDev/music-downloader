import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel,QFileDialog,QComboBox, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtCore import QUrl

from src.core.downloader import *

def main():
    app = QApplication(sys.argv)
    with open('resources/styles/styles.css', 'r') as f:
        styles = f.read()
        app.setStyleSheet(styles)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

class PreviewCover(QThread):
    info_ready = pyqtSignal(dict)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            from src.core.downloader import get_media_info
            info = get_media_info(self.url)
            self.info_ready.emit(info)
        except Exception as e:
            print(f"Error getting info {e}")

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
        self.setObjectName("MainWindow")
        self.startUI()

    # Interface
    def startUI(self):
        self.setFixedSize(410, 600)
        self.setWindowTitle('MusicDownloader')
        self.interface()
        self.show()

    def interface(self):        
        self.label_image = QLabel('')
        self.label_image.setMaximumSize(380, 200)
        self.label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_image.hide()

        self.label_title = QLabel('')
        self.label_title.setWordWrap(True)
        self.label_title.setMaximumHeight(40)
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_title.hide()

        self.input_link = QLineEdit(self)
        self.input_link.setPlaceholderText("Paste link here")

        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.load_preview)
        self.input_link.textChanged.connect(self.on_text_changed)

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
        h_layout0 = QHBoxLayout()
        h_layout1 = QHBoxLayout()
        h_layout2 = QHBoxLayout()
        h_layout3 = QHBoxLayout()
        h_layout4 = QHBoxLayout()
        h_layout0.addWidget(self.label_image)
        h_layout1.addWidget(self.label_title)
        h_layout2.addWidget(self.input_link)
        h_layout2.addWidget(self.button_download)
        h_layout3.addWidget(self.media_selector)
        h_layout3.addWidget(self.format_selector)
        h_layout4.addWidget(self.directory_selector)
        GeneralLayout.addLayout(h_layout0)
        GeneralLayout.addLayout(h_layout1)
        GeneralLayout.addLayout(h_layout2)
        GeneralLayout.addLayout(h_layout3)
        GeneralLayout.addLayout(h_layout4)
        self.setLayout(GeneralLayout)

    # Logic
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.loaded_cover)

    def show_cover(self, urls):
        request = QNetworkRequest(QUrl(urls))
        self.network_manager.get(request)

    def loaded_cover(self, reply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data_image = reply.readAll()
            image = QImage()
            image.loadFromData(data_image)
            pixmap = QPixmap.fromImage(image)
            self.label_image.setPixmap(pixmap)
            pixmap = pixmap.scaledToWidth(380, Qt.TransformationMode.SmoothTransformation)
            self.label_image.setPixmap(pixmap)
            self.label_image.show()
            self.label_title.show()
        else: 
            self.label_image.hide()
            self.label_title.hide()
            self.label_image.setText('Error: Image not found')
            reply.deleteLater()

    def on_text_changed(self, text):
        if len(text) > 10:
            self.preview_timer.start(100) # 800ms wait
        else:
            self.preview_timer.stop()

    def load_preview(self):
        url = self.input_link.text()
        self.preview_thread = PreviewCover(url)
        self.preview_thread.info_ready.connect(self.show_preview)
        self.preview_thread.start()

    def show_preview(self, info):
        self.label_title.setText(info['title'])
        self.show_cover(info['thumbnail'])

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
        if os.path.exists('.config/config.json'):
            with open('.config/config.json', 'r') as archive:
                data = json.load(archive)
                path = data['last_directory']
            self.directory_selected = path
        else:
            self.directory_selected = ''


    def save_directory(self):
        if not os.path.exists('.config'):
            os.makedirs('.config')
        dictionary = {"last_directory": self.directory_selected}

        with open('.config/config.json', 'w') as archive:
            json.dump(dictionary, archive, indent=4)
            print("Path saved")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    sys.exit(app.exec())