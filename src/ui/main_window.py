import sys
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QPushButton, QLabel, QFileDialog,
    QComboBox, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QPixmap, QImage, QFontDatabase, QDesktopServices, QIcon
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from src.core.workers import PreviewCover, DownloadThread
from src.core.settings import read_directory, save_directory
from src.ui.components.playlist_item import PlaylistItemWidget


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


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.startUI()

    def startUI(self):
        self.setFixedSize(430, 660)
        self.setWindowTitle('MusicDownloader')
        self.interface()
        self.show()

    def interface(self):
        self.lbl_default_image1 = QLabel('')
        pixmap_default_img1 = QPixmap('resources/icons/musicalNotes.png')
        pixmap_default_img1 = pixmap_default_img1.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_default_image1.setPixmap(pixmap_default_img1)
        self.lbl_default_image1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_default_image1.setObjectName('lblDefaultImage1')

        self.lbl_default_text1 = QLabel('Paste a video link \nto preview and download media')
        self.lbl_default_text1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_default_text1.setObjectName('lblDefaultText1')

        self.lbl_cover = QLabel('')
        self.lbl_cover.setMaximumSize(380, 250)
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

        self.button_playlist_expand = QPushButton('Playlist', self)
        self.button_playlist_expand.setFixedSize(80, 35)
        self.button_playlist_expand.clicked.connect(self.playlist_interaction)
        self.button_playlist_expand.setObjectName('buttonPlaylist')

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

        icon_download = QIcon('resources/icons/download.png')
        self.button_download.setIcon(icon_download)

        self.lbl_format = QLabel('Format')

        self.media_selector = QComboBox(self)
        self.media_selector.addItems(['Audio', 'Video'])
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

        # Read the saved directory using settings.py
        self.directory_selected = read_directory()
        if self.directory_selected:
            self.directory_direction.setPlaceholderText(self.directory_selected)

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
        self.container_layout1.setFixedHeight(90)
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

        self.container_playlist = QWidget()
        self.container_playlist.setObjectName('containerPlaylist')
        self.container_playlist.hide()

        self.container_layout2 = QWidget()
        self.container_layout2.setObjectName('containerLayout2')
        self.container_layout2.setMinimumHeight(125)
        v_layout2 = QVBoxLayout(self.container_layout2)
        layout2row1 = QHBoxLayout()
        layout2row2 = QHBoxLayout()
        layout2row3 = QHBoxLayout()
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
        layout1row3.addWidget(self.button_playlist_expand)

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
        GeneralLayout.addSpacing(2)
        GeneralLayout.addWidget(self.container_layout1)
        GeneralLayout.addSpacing(8)
        GeneralLayout.addWidget(self.container_playlist, stretch=1)
        GeneralLayout.addWidget(self.container_layout2)
        GeneralLayout.addSpacing(8)
        GeneralLayout.addWidget(self.container_layout3)
        GeneralLayout.addWidget(self.container_layout4)
        GeneralLayout.addStretch()

        self.setLayout(GeneralLayout)

        # Network administrator for uploading cover images
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.loaded_cover)

    # Cover logic
    def show_cover(self, url):
        request = QNetworkRequest(QUrl(url))
        self.network_manager.get(request)

    def loaded_cover(self, reply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data_image = reply.readAll()
            image = QImage()
            image.loadFromData(data_image)
            pixmap = QPixmap.fromImage(image)
            pixmap = pixmap.scaled(380, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.lbl_cover.setPixmap(pixmap)
            self.lbl_cover.show()
            self.container_cover.show()
            self.container_layout0.hide()
            self.container_layout1.show()
        else:
            self.lbl_cover.hide()
            self.lbl_cover.setText('Error: Image not found')
            reply.deleteLater()

    # Preview
    def on_text_changed(self, text):
        if len(text) > 10:
            self.preview_timer.start(100)
        else:
            self.preview_timer.stop()

    def load_preview(self):
        url = self.input_link.text()
        if '&list=' in url:
            url = url.split('&list=')[0]
            self.button_playlist_expand.show()
        else:
            self.button_playlist_expand.hide()
        self.preview_thread = PreviewCover(url)
        self.preview_thread.info_ready.connect(self.show_preview)
        self.preview_thread.start()

    def show_preview(self, info):
        self.show_cover(info.get('thumbnail', ''))
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
                self.lbl_date_info.setText(obj_date.strftime("%d %b %Y"))
            except ValueError:
                self.lbl_date_info.setText(simple_date)
        else:
            self.lbl_date_info.setText("Unknown date")

    # Format selector
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

    # Download
    def download_media(self):
        link = self.input_link.text()
        if not link:
            print("Put a valid URL")
            return
        self.download_thread = DownloadThread(
            urls=[link],
            selected_format=self.format_selector.currentText(),
            selected_media=self.selected_media,
            directory_selected=self.directory_selected,
        )
        self.download_thread.start()
        print("Download started in the background")

    # Folder
    def choose_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Choose carpet')
        if directory:
            self.directory_selected = directory
            save_directory(directory)
            self.directory_direction.setText(directory)

    def open_download_folder(self):
        path = self.directory_selected
        if path and os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            print("Error: You haven't selected a download path yet, or the selected path doesn't exist.")

    # Playlist
    def playlist_interaction(self):
        if self.container_playlist.isHidden():
            self.container_playlist.show()
            self.container_layout2.hide()
            self.container_layout3.hide()
            self.container_layout4.hide()
        else:
            self.container_playlist.hide()
            self.container_layout2.show()
            self.container_layout3.show()
            self.container_layout4.show()