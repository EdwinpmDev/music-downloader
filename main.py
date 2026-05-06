# Librerias / libraries
import yt_dlp
from yt_dlp import YoutubeDL

# Estructura
def descarga_video(urls_video: list):
    with YoutubeDL() as ydl:
        ydl.download(urls_video)


def descarga_audio(urls_audio: list, selected_format: str):
    ydl_opts = {
        'format': f'{selected_format}/bestaudio/best',

        'postprocessors': [{  
        'key': 'FFmpegExtractAudio',
        'preferredcodec': selected_format,
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(urls_audio)