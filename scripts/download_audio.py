import yt_dlp
import os
from scripts.exception import MyException
from scripts.logger import logging

def download_audio(youtube_url, custom_title, output_folder="downloads/raw_audio"):
    try:
        # Validate YouTube URL
        if not youtube_url or not youtube_url.startswith("http"):
            logging.error("Invalid YouTube URL provided.")
            raise ValueError("Invalid YouTube URL. Please provide a valid URL.")

        # Ensure the output folder exists
        os.makedirs(output_folder, exist_ok=True)

        # Sanitize title to create a valid filename
        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in custom_title.strip())
        output_path = os.path.join(output_folder, f"{safe_title}.mp3")

        # Validate output folder permissions
        if not os.access(output_folder, os.W_OK):
            logging.error(f"Output folder is not writable: {output_folder}")
            raise PermissionError(f"Cannot write to output folder: {output_folder}")

        # yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,  
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        # Download audio using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        logging.info(f"YouTube audio downloaded successfully: {output_path}")

        return output_path

    except yt_dlp.utils.DownloadError as e:
        logging.error(f"Download error: {e}")
        raise MyException(f"Failed to download audio: {e}")
    except Exception as e:
        logging.error(f"Error downloading audio: {e}")
        raise MyException(e)