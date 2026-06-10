# libraries / Librerias
import os
import shutil
import yt_dlp
from yt_dlp import YoutubeDL

# Media framework search
def get_ffmpeg_path():
    # Dynamic search
    dynamic_path = shutil.which('ffmpeg')
    if dynamic_path:
        return dynamic_path
    
    # Manual search
    if os.name == 'nt': # Windows
        common_paths = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\FFmpeg\bin\ffmpeg.exe',
            r'C:\ProgramData\chocolatey\bin\ffmpeg.exe'
        ]
    else:
        common_paths = [
                    '/usr/bin/ffmpeg',
                    '/usr/local/bin/ffmpeg',
                    '/opt/homebrew/bin/ffmpeg'
                ]
    for path in common_paths:
        if os.path.exists(path):
            return path
        
    # Fallback
    return 'ffmpeg'
#Initialize global variable
ffmpeg_location = get_ffmpeg_path()

# Get media info
def get_media_info(url: str) -> dict:
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    } 
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info=ydl.extract_info(url, download=False)
        return{
            'title': info.get('title', 'No title'),
            'thumbnail': info.get('thumbnail', '')
        }

# Structure / Estructura
def download_any_media(
        urls: list,
        selected_format: str,
        selected_media: str,
        directory_selected: str
):

    ydl_opts = {
        'ffmpeg_location': ffmpeg_location
    }

    if directory_selected:
        ydl_opts['outtmpl'] = os.path.join(
            directory_selected,
            '%(title)s.%(ext)s'
        )

    if selected_media == "Audio":

        ydl_opts.update({
            'format': f'{selected_format}/bestaudio/best',
            'writethumbnail': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': selected_format
                },
                {
                    'key': 'FFmpegThumbnailsConvertor',
                    'format': 'jpg'
                },
                {
                    'key': 'EmbedThumbnail'
                },
                {
                    'key': 'FFmpegMetadata'
                }
            ]
        })

    else:

        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': selected_format
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download(urls)

        if error_code != 0:
            print("Error download")
        else:
            print("Successful download")

    except Exception as e:
        print(f"Download failed: {e}")