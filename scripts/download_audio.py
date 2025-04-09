import os
import sys
import shutil
import re
import subprocess
import yt_dlp
from scripts.exception import MyException
from scripts.logger import logging


def sanitize_filename(name):
    """Sanitize the custom title to create a valid filename."""
    return re.sub(r'[\\/*?:"<>|]', "_", name.strip())


def get_unique_filename(path):
    """Generate a unique filename if file already exists."""
    base, ext = os.path.splitext(path)
    counter = 1
    while os.path.exists(path + ".mp3") or os.path.exists(path):
        path = f"{base}_{counter}{ext}"
        counter += 1
    return path


def progress_hook(d):
    """Hook to log yt-dlp progress."""
    if d['status'] == 'finished':
        logging.info("Download complete, converting...")


def has_audio_stream(filepath):
    """Check if the file has an audio stream using ffprobe."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'a',
             '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', filepath],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout.strip() != ''
    except Exception as e:
        logging.error(f"ffprobe error: {e}")
        return False


def download_audio(youtube_url, custom_title, output_folder="downloads/raw_audio"):
    try:
        if not youtube_url or not youtube_url.startswith("http"):
            logging.error("Invalid YouTube URL provided.")
            raise ValueError("Invalid YouTube URL. Please provide a valid URL.")

        os.makedirs(output_folder, exist_ok=True)

        safe_title = sanitize_filename(custom_title)
        output_path = os.path.join(output_folder, f"{safe_title}")
        output_path = get_unique_filename(output_path)

        if not os.access(output_folder, os.W_OK):
            logging.error(f"Output folder is not writable: {output_folder}")
            raise PermissionError(f"Cannot write to output folder: {output_folder}")

        # STEP 1: Pre-check if the video has audio stream using metadata
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            if 'acodec' in info and info['acodec'] == 'none':
                logging.warning("Video has no audio stream, skipping download.")
                raise MyException("The video has no audio stream to extract.", sys)

        # STEP 2: yt-dlp options to download and convert to mp3
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path + ".%(ext)s",
            'ffmpeg_location': r'C:\ffmpeg\bin',
            'prefer_ffmpeg': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [progress_hook],
            'quiet': False,
            'noplaylist': True,
        }

        # STEP 3: Download and extract
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)

        # Final MP3 file path
        final_path = f"{os.path.splitext(output_path)[0]}.mp3"

        # STEP 4: Validate the resulting mp3 file (instead of webm)
        if not has_audio_stream(final_path):
            logging.warning("Converted MP3 has no audio stream.")
            raise MyException("The extracted audio file has no valid audio stream.", sys)

        logging.info(f"YouTube audio downloaded successfully: {final_path}")
        return final_path

    except yt_dlp.utils.DownloadError as e:
        logging.error(f"Download error: {e}")
        raise MyException(str(e), sys)
    except Exception as e:
        logging.error(f"Error downloading audio: {e}")
        raise MyException(str(e), sys)


# if __name__ == "__main__":
#     youtube_url = input("Enter YouTube URL: ")
#     custom_title = input("Enter custom title: ")
#     download_audio(youtube_url, custom_title)
