# import json
# import os
# from scripts.download_audio import download_audio
# from scripts.transcribe import transcribe_audio, generate_summary
# from scripts.save_json import save_transcript_and_summary

# def process_video(video_title, url, output_folder="downloads"):
#     """
#     Processes a YouTube video by downloading audio, transcribing it, generating a summary,
#     and saving the results to a JSON file.
#     """
#     try:
#         if not video_title or not url:
#             raise ValueError("Video title and URL cannot be empty.")

#         os.makedirs(output_folder, exist_ok=True)  # Ensure folder exists

#         # Step 1: Download Audio
#         audio_path = download_audio(youtube_url=url, custom_title=video_title, output_folder=output_folder)
        
#         if not audio_path or not os.path.exists(audio_path):
#             raise FileNotFoundError("Audio download failed.")

#         # Step 2: Transcribe Audio
#         transcription = transcribe_audio(audio_path=audio_path)
#         if not transcription:
#             raise ValueError("Transcription not created. Check the transcription function.")

#         # Step 3: Generate Summary
#         summary = generate_summary(transcription)
#         if not summary:
#             raise ValueError("Summary not created. Check the summary function.")

#         # Step 4: Save Results
#         save_transcript_and_summary(video_title=video_title, transcript=transcription, summary=summary)

#         print(f"✅ Transcription and summary saved for {video_title}")

#     except Exception as e:
#         print(f"❌ Error: {e}")

# if __name__ == "__main__":
#     video_title = input("Enter video title: ").strip()
#     url = input("Enter video URL: ").strip()
#     process_video(video_title, url)


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
        raise  MyException(e , sys)


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
    app.run(host="0.0.0.0", port=port)