from PyQt6.QtCore import QThread, pyqtSignal

from src.core.downloader import (
    get_media_info,
    download_any_media,
)


class PreviewCover(QThread):
    info_ready = pyqtSignal(dict)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            info = get_media_info(self.url)
            self.info_ready.emit(info)
        except Exception as e:
            print(f"Error getting info: {e}")


class DownloadThread(QThread):
    def __init__(
        self,
        urls,
        selected_format,
        selected_media,
        directory_selected,
    ):
        super().__init__()
        self.urls = urls
        self.selected_format = selected_format
        self.selected_media = selected_media
        self.directory_selected = directory_selected

    def run(self):
        try:
            download_any_media(
                self.urls,
                self.selected_format,
                self.selected_media,
                self.directory_selected,
            )
        except Exception as e:
            print(f"Download error: {e}")