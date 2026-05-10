# libraries / Librerias
import os
import yt_dlp
from yt_dlp import YoutubeDL

# Media framework
ffmpeg_location = '/usr/bin/ffmpeg'

'''
ffmpeg_location = [
    '/usr/bin/ffmpeg',
    '/usr/local/bin/ffmpeg',
    'C:\Program Files\FFmpeg\bin\ffmpeg.exe',
]
'''

# Structure / Estructura
def download_any_media(urls: list, selected_format: str, selected_media: str, directory_selected: str):
    if selected_media == "Audio":
        if directory_selected == '':
            ydl_opts = {
                'format': f'{selected_format}/bestaudio/best',
                'ffmpeg_location': ffmpeg_location,
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
                'format': f'{selected_format}/bestaudio/best',
                'outtmpl': f'{directory_selected}/%(title)s.%(ext)s',
                'ffmpeg_location': ffmpeg_location,
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
        if directory_selected == '':
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'ffmpeg_location': ffmpeg_location,
                'merge_output_format': selected_format
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
                'ffmpeg_location': ffmpeg_location,
                'outtmpl': f'{directory_selected}/%(title)s.%(ext)s'
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                error_code = ydl.download(urls)

                if error_code !=0:
                    print("Error download")
                else:
                    print("Succesful download")