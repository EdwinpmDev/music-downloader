from PyQt6.QtWidgets import QWidget


class PlaylistItemWidget(QWidget):
    def __init__(
        self,
        thumbnail_url,
        title,
        channel,
        duration,
        parent=None,
    ):
        super().__init__(parent)

        self.thumbnail_url = thumbnail_url
        self.title = title
        self.channel = channel
        self.duration = duration

        self.setObjectName("playlistItemWidget")