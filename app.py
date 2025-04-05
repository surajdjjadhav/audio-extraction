import os
from scripts.logger import logging
from scripts.exception import MyException
from flask import Flask, request, render_template
from scripts.download_audio import download_audio
from scripts.transcribe import HindiTranscriber
from scripts.save_json import save_transcript_and_summary
import sys

app = Flask(__name__)

def process_video(video_title, url):
    """
    Processes the video: downloads audio, transcribes it, generates a summary, and saves results.
    """
    try:
        if not video_title or not url:
            raise ValueError("Video title and URL are required.")

        logging.info(f"Downloading audio for: {video_title}")
        audio_path = download_audio(url, video_title)
        if not os.path.exists(audio_path):
            raise FileNotFoundError("Failed to download audio.")

        logging.info("Initializing transcriber...")
        transcriber = HindiTranscriber(model_size="medium")  # Adjust model size if needed

        logging.info("Processing transcription...")
        final_transcription, summary = transcriber.process_audio(audio_path, output_dir="downloads/transcribed_text")

        logging.info("Saving transcript and summary...")
        save_transcript_and_summary(video_title, final_transcription, summary)

        return final_transcription, summary

    except Exception as e:
        logging.error(f"Error processing video: {e}")
        raise MyException(e, sys)

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Handles the main page and form submission.
    """
    if request.method == "POST":
        video_title = request.form.get("video_title", "").strip()
        url = request.form.get("video_url", "").strip()

        if not video_title or not url:
            return render_template("index.html", error="Video title and URL are required.")

        try:
            transcription, summary = process_video(video_title, url)

            return render_template(
                "index.html",
                message="Processing complete!",
                video_title=video_title,
                transcription=transcription,
                summary=summary
            )
        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")

# Gunicorn entry point
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Default to 5000
    app.run(debug=True, host="0.0.0.0", port=port)