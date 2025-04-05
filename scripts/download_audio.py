import yt_dlp
import os
from scripts.exception import MyException
from scripts.logger import logging

def download_audio(youtube_url, custom_title, output_folder="downloads/raw_audio"):
    try:
        # Ensure the output folder exists
        os.makedirs(output_folder, exist_ok=True)

        # Remove # and sanitize title
        safe_title = custom_title.replace("#", "").strip()
        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in safe_title)
        
        output_path = os.path.join(output_folder, f"{safe_title}.mp3")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,  
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        logging.info(f"YouTube audio downloaded successfully: {output_path}")

        return output_path

    except Exception as e:
        logging.error(f"Error downloading audio: {e}")
        raise MyException(e)