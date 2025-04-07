import os
import sys
import shutil
import re
import yt_dlp
from scripts.exception import MyException
from scripts.logger import logging


def check_dependencies():
    """Check if required dependencies are installed."""
    # Check if FFmpeg is installed
    if shutil.which('ffmpeg') is None:
        logging.error("FFmpeg is not installed. Please install FFmpeg to extract audio.")
        raise EnvironmentError("FFmpeg is not installed. Please install FFmpeg to extract audio.")


def sanitize_filename(name):
    """Sanitize the custom title to create a valid filename."""
    return re.sub(r'[\\/*?:"<>|]', "_", name.strip())


def get_unique_filename(path):
    """Generate a unique filename if file already exists."""
    base, ext = os.path.splitext(path)
    counter = 1
    while os.path.exists(path):
        path = f"{base}_{counter}{ext}"
        counter += 1
    return path


def progress_hook(d):
    """Hook to log yt-dlp progress."""
    if d['status'] == 'finished':
        logging.info("Download complete, converting...")


def download_audio(youtube_url, custom_title, output_folder="downloads/raw_audio"):
    try:
        # Check dependencies
        check_dependencies()

        # Validate YouTube URL
        if not youtube_url or not youtube_url.startswith("http"):
            logging.error("Invalid YouTube URL provided.")
            raise ValueError("Invalid YouTube URL. Please provide a valid URL.")

        # Ensure the output folder exists
        os.makedirs(output_folder, exist_ok=True)

        # Sanitize title and generate output path
        safe_title = sanitize_filename(custom_title)
        output_path = os.path.join(output_folder, f"{safe_title}.mp3")
        output_path = get_unique_filename(output_path)

        # Check write permissions
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
            'progress_hooks': [progress_hook],
        }

        # Download audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        logging.info(f"YouTube audio downloaded successfully: {output_path}")
        return output_path

    except yt_dlp.utils.DownloadError as e:
        logging.error(f"Download error: {e}")
        raise MyException(str(e), sys.exc_info())
    except Exception as e:
        logging.error(f"Error downloading audio: {e}")
        raise MyException(str(e), sys.exc_info())
