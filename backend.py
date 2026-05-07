# libraries / Librerias
import yt_dlp
from yt_dlp import YoutubeDL

# Structure / Estructura
def download_any_media(urls: list, selected_format: str, selected_media: str):
    if selected_media == "Audio":
        ydl_opts = {
            'format': f'{selected_format}/bestaudio/best',

            'postprocessors': [{  
            'key': 'FFmpegExtractAudio',
            'preferredcodec': selected_format,
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download(urls)

            if error_code !=0:
                print("Error download")
            else:
                print("Succesful download")
    else:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': selected_format,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download(urls)

            if error_code !=0:
                print("Error download")
            else:
                print("Succesful download")