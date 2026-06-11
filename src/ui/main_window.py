import sys
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel,QFileDialog,QComboBox, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QImage, QFontDatabase, QDesktopServices, QIcon
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtCore import QUrl

from src.core.downloader import *

def main():
    app = QApplication(sys.argv)
    font_id = QFontDatabase.addApplicationFont("resources/fonts/Inter_18pt-Regular.ttf")
    if font_id == -1:
        print("Error: The font could not be loaded -> Inter.")

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
        self.setFixedSize(420, 660)
        self.setWindowTitle('MusicDownloader')
        self.interface()
        self.show()

    def interface(self):
        self.lbl_default_image1 = QLabel('')
        pixmap_default_img1 = QPixmap('resources/icons/whiteLink.png')
        pixmap_default_img1 = pixmap_default_img1.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_default_image1.setPixmap(pixmap_default_img1)
        self.lbl_default_image1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_default_image1.setObjectName('lblDefaultImage1')

        self.lbl_default_text1 = QLabel('Paste a video link \nto preview and download media')
        self.lbl_default_text1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_default_text1.setObjectName('lblDefaultText1')

        '''self.lbl_default_image2 = QLabel('')
        pixmap_default_img2 = QPixmap('resources/icons/clock.png')
        pixmap_default_img2 = pixmap_default_img2.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_default_image2.setPixmap(pixmap_default_img2)

        self.lbl_default_text2 = QLabel('Paste a valid video link \nto see video information') '''


        self.lbl_cover = QLabel('')
        self.lbl_cover.setMaximumSize(380, 200)
        self.lbl_cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_cover.hide()

        self.lbl_img_info = QLabel(self)
        self.lbl_img_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title_info = QLabel('-')
        self.lbl_title_info.setObjectName('lblTitleVideo')
        self.lbl_channel_info = QLabel('-')
        self.lbl_channel_info.setObjectName('lblChannelInfo')

        self.lbl_duration_img = QLabel('time')
        pixmap_time = QPixmap('resources/icons/clock.png')
        pixmap_time = pixmap_time.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_duration_img.setPixmap(pixmap_time)

        self.lbl_time_info = QLabel('0:00')
        self.lbl_time_info.setObjectName('lblTimeInfo')

        self.lbl_date_img = QLabel('date')
        pixmap_calendar = QPixmap('resources/icons/calendar.png')
        pixmap_calendar = pixmap_calendar.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_date_img.setPixmap(pixmap_calendar)

        self.lbl_date_info = QLabel('1 jan. 2004')
        self.lbl_date_info.setObjectName('lblDateInfo')

        self.input_link = QLineEdit(self)
        self.input_link.setPlaceholderText("Paste link here")
        icon_link = QIcon('resources/icons/link.png')
        self.input_link.addAction(icon_link, QLineEdit.ActionPosition.LeadingPosition)

        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.load_preview)
        self.input_link.textChanged.connect(self.on_text_changed)

        self.button_download = QPushButton('  Download', self)
        self.button_download.clicked.connect(self.download_media)
        self.button_download.setObjectName('downloadButton')

        self.lbl_download_image = QLabel('')
        icon_download = QIcon('resources/icons/download.png')
        self.button_download.setIcon(icon_download)

        self.lbl_format = QLabel('Format')

        self.media_selector = QComboBox(self)
        self.media_selector.addItems(['Audio','Video'])
        self.media_selector.currentTextChanged.connect(self.media_change)

        self.lbl_quality = QLabel('Quality')

        self.format_selector = QComboBox(self)

        self.lbl_folder = QLabel('Download folder')

        self.directory_direction = QLineEdit(self)
        self.directory_direction.setReadOnly(True)
        self.directory_direction.setPlaceholderText('No directory selected')
        icon_folder = QIcon('resources/icons/folder.png')
        self.directory_direction.addAction(icon_folder, QLineEdit.ActionPosition.LeadingPosition)

        self.directory_open = QPushButton('Open')
        self.directory_open.setObjectName("directoryOpen")
        self.directory_open.clicked.connect(self.open_download_folder)

        self.directory_selector = QPushButton('Select download directory', self)
        self.directory_selector.clicked.connect(self.choose_directory)
        self.directory_selector.setObjectName("directorySelector")

        self.directory_selected = ''
        self.read_directory()
        self.media_change()

        self.lbl_language = QLabel('Made with 💚 using Python |')

        self.lbl_cli_image = QLabel('')
        pixmap_cli = QPixmap('resources/icons/whiteLink.png')
        pixmap_cli = pixmap_cli.scaled(10, 10, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_cli_image.setPixmap(pixmap_cli)
        self.lbl_cli = QLabel('yt-dlp |')

        self.lbl_wrapper_image = QLabel('')
        pixmap_wrapper = QPixmap('resources/icons/soundWave.png')
        pixmap_wrapper = pixmap_wrapper.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_wrapper_image.setPixmap(pixmap_wrapper)
        self.lbl_wrapper = QLabel('FFmpeg |')

        self.lbl_fmwork_image = QLabel('')
        pixmap_qt = QPixmap('resources/icons/qt.png')
        pixmap_qt = pixmap_qt.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_fmwork_image.setPixmap(pixmap_qt)
        self.lbl_framework = QLabel('PyQt6')

        # Layout
        GeneralLayout = QVBoxLayout()
        GeneralLayout.addStretch()

        self.container_cover = QWidget()
        cover_layout = QHBoxLayout(self.container_cover)
        self.container_cover.hide()
        
        self.container_layout0 = QWidget()
        self.container_layout0.setObjectName('containerLayout0')
        h_layout0 = QVBoxLayout(self.container_layout0)
        QstackedWidgets = QVBoxLayout()
        Qsignalponts = QHBoxLayout()
        h_layout0.addLayout(QstackedWidgets)
        h_layout0.addLayout(Qsignalponts) 
        Qstackedrow1 = QHBoxLayout()
        Qstackedrow2 = QHBoxLayout()
        QstackedWidgets.addLayout(Qstackedrow1)
        QstackedWidgets.addLayout(Qstackedrow2)


        self.container_layout1 = QWidget()
        self.container_layout1.setObjectName('containerLayout1')
        self.container_layout1.hide()
        h_layout1 = QHBoxLayout(self.container_layout1)
        self.container_qhbox_layout1 = QWidget()
        self.container_qhbox_layout1.setObjectName('qhbox_layout1')
        intern_qhbox_layout1 = QHBoxLayout(self.container_qhbox_layout1)
        intern_qvbox_layout1 = QVBoxLayout()
        layout1row1 = QHBoxLayout()
        layout1row2 = QHBoxLayout()
        layout1row3 = QHBoxLayout()
        layout1row3.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout1row3.setSpacing(5)
        h_layout1.addWidget(self.container_qhbox_layout1)
        h_layout1.addLayout(intern_qvbox_layout1)
        intern_qvbox_layout1.addLayout(layout1row1)
        intern_qvbox_layout1.addLayout(layout1row2)
        intern_qvbox_layout1.addLayout(layout1row3)

        self.container_layout2 = QWidget()
        self.container_layout2.setObjectName('containerLayout2')
        self.container_layout2.setMinimumHeight(125)
        v_layout2 = QVBoxLayout(self.container_layout2)
        layout2row1 = QHBoxLayout()
        layout2row2 = QHBoxLayout()
        layout2row3  = QHBoxLayout()
        v_layout2.addLayout(layout2row1)
        v_layout2.addLayout(layout2row2)
        v_layout2.addLayout(layout2row3)

        self.container_layout3 = QWidget()
        self.container_layout3.setObjectName('containerLayout3')
        self.container_layout3.setMinimumHeight(130)
        v_layout3 = QVBoxLayout(self.container_layout3)
        layout3row1 = QHBoxLayout()
        layout3row2 = QHBoxLayout()
        layout3row3 = QHBoxLayout()
        v_layout3.addLayout(layout3row1)
        v_layout3.addLayout(layout3row2)
        v_layout3.addLayout(layout3row3)

        self.container_layout4 = QWidget()
        self.container_layout4.setObjectName('containerLayout4')
        self.container_layout4.setMinimumHeight(50)
        h_layout4 = QHBoxLayout(self.container_layout4)

        cover_layout.addWidget(self.lbl_cover)

        #h_layout0.addWidget(self.lbl_cover)
        QstackedWidgets.setAlignment(Qt.AlignmentFlag.AlignCenter)
        Qstackedrow1.addWidget(self.lbl_default_image1)
        Qstackedrow1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        Qstackedrow2.addWidget(self.lbl_default_text1)
        Qstackedrow2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        intern_qhbox_layout1.addWidget(self.lbl_img_info)
        layout1row1.addWidget(self.lbl_title_info)
        layout1row2.addWidget(self.lbl_channel_info)
        layout1row3.addWidget(self.lbl_duration_img)
        layout1row3.addWidget(self.lbl_time_info)
        layout1row3.addSpacing(30)
        layout1row3.addWidget(self.lbl_date_img)
        layout1row3.addWidget(self.lbl_date_info)
        layout1row3.addStretch()

        layout2row1.addWidget(self.input_link)
        layout2row1.addWidget(self.button_download)
        layout2row2.addWidget(self.lbl_format)
        layout2row2.addWidget(self.lbl_quality)
        layout2row3.addWidget(self.media_selector)
        layout2row3.addWidget(self.format_selector)

        layout3row1.addWidget(self.lbl_folder)
        layout3row2.addWidget(self.directory_direction)
        layout3row2.addWidget(self.directory_open)
        layout3row3.addWidget(self.directory_selector)

        h_layout4.addWidget(self.lbl_language)
        h_layout4.addWidget(self.lbl_cli_image)
        h_layout4.addWidget(self.lbl_cli)
        h_layout4.addWidget(self.lbl_wrapper_image)
        h_layout4.addWidget(self.lbl_wrapper)
        h_layout4.addWidget(self.lbl_fmwork_image)
        h_layout4.addWidget(self.lbl_framework)
        h_layout4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout4.setSpacing(4)
        h_layout4.setContentsMargins(0, 0, 0, 0)

        GeneralLayout.addWidget(self.container_cover)
        GeneralLayout.addWidget(self.container_layout0, stretch=1)
        GeneralLayout.addSpacing(8)
        GeneralLayout.addWidget(self.container_layout1)
        GeneralLayout.addSpacing(8)
        GeneralLayout.addWidget(self.container_layout2)
        GeneralLayout.addSpacing(8)
        GeneralLayout.addWidget(self.container_layout3)
        GeneralLayout.addWidget(self.container_layout4)

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
            self.lbl_cover.setPixmap(pixmap)
            pixmap = pixmap.scaledToWidth(380, Qt.TransformationMode.SmoothTransformation)
            self.lbl_cover.setPixmap(pixmap)
            self.lbl_cover.show()
            self.container_cover.show()
            self.container_layout0.hide()
            self.container_layout1.show()
        else: 
            self.lbl_cover.hide()
            self.lbl_cover.setText('Error: Image not found')
            reply.deleteLater()

    def on_text_changed(self, text):
        if len(text) > 10:
            self.preview_timer.start(100) # ms wait
        else:
            self.preview_timer.stop()

    def load_preview(self):
        url = self.input_link.text()
        if '&list=' in url:
            url = url.split('&list=')[0]
        self.preview_thread = PreviewCover(url)
        self.preview_thread.info_ready.connect(self.show_preview)
        self.preview_thread.start()

    def show_preview(self, info):
        self.show_cover(info.get('thumbnail',''))
        self.lbl_title_info.setText(info.get('title', 'Unknown title'))
        canal = info.get('channel') or info.get('uploader') or 'Unknown channel'
        self.lbl_channel_info.setText(canal)
        if info.get('duration_string'):
            self.lbl_time_info.setText(info.get('duration_string'))
        elif info.get('duration'):
            segs = int(info.get('duration'))
            minutes, seconds = divmod(segs, 60)
            self.lbl_time_info.setText(f"{minutes}:{seconds:02d}")
        else:
            self.lbl_time_info.setText('0:00')
        simple_date = info.get('upload_date')
        if simple_date:
            try:
                obj_date = datetime.strptime(simple_date, "%Y%m%d")
                final_date = obj_date.strftime("%d %b %Y")
                self.lbl_date_info.setText(final_date)
            except ValueError:
                self.lbl_date_info.setText(simple_date)
        else:
            self.lbl_date_info.setText("Unknown date")
        

    def media_change(self):
        self.format_selector.clear()
        self.selected_media = self.media_selector.currentText()

        if self.selected_media == "Audio":
            self.format_selector.addItems(['mp3', 'aac', 'opus', 'm4a', 'ogg', 'webm'])
            pixmap = QPixmap('resources/icons/musicplayer.png')
        else:
            self.format_selector.addItems(['mp4', 'm4a', 'webm'])
            pixmap = QPixmap('resources/icons/videoplayer.png')
        pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_img_info.setPixmap(pixmap)


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
            self.directory_direction.setText(directory)



    def read_directory(self):
        if os.path.exists('.config/config.json'):
            with open('.config/config.json', 'r') as archive:
                data = json.load(archive)
                path = data['last_directory']
                self.directory_direction.setPlaceholderText(f'{path}')
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

    def open_download_folder(self):
        path = self.directory_selected
        if path and os.path.exists(path):
            local_url = QUrl.fromLocalFile(path)
            QDesktopServices.openUrl(local_url)
        else:
            print("Error: You haven't selected a download path yet, or the selected path doesn't exist.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    sys.exit(app.exec())