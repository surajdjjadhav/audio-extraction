import json
import os
import sys
from scripts.exception import MyException
from scripts.logger import logging
from scripts.transcribe import HindiTranscriber

def save_transcript_and_summary(video_title, transcript, summary, output_folder="downloads/json_files/"):
    """
    Saves video transcript and summary to a JSON file.
    Each video will be saved in a separate file named after the video title.
    """
    try:
        logging.info(f"Starting to save transcript and summary for: {video_title}")

        # Ensure the folder exists
        os.makedirs(output_folder, exist_ok=True)

        # Sanitize video title to create a valid filename
        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in video_title)
        output_file = os.path.join(output_folder, f"{safe_title}.json")

        # Prepare the data to be saved
        data = {
            "title": video_title,
            "summary": summary,
            "transcript": transcript
        }

        # Save the data as a single JSON object
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        logging.info(f"✅ Transcript and summary saved successfully to: {output_file}")
        return output_file

    except Exception as e:
        logging.error(f"❌ Error saving transcript and summary: {e}")
        raise MyException(f"Failed to save transcript and summary: {e}", sys)
    



if __name__ == "__main__":
    try:
        model_choice = input("🧠 Choose Whisper model size (tiny/base/small/medium/large): ").strip().lower()

        if model_choice not in ['tiny', 'base', 'small', 'medium', 'large']:
            print("⚠️ Invalid model selected. Using default: base")
            model_choice = "base"

        file_path = "downloads/raw_audio/suraj.mp3"

        transcriber = HindiTranscriber(audio_file=file_path, model_size=model_choice)
        clean_text, summary = transcriber.process_audio("downloads/transcribed_text")
        save_transcript_and_summary("Suraj", clean_text, summary)
    except Exception as e:
        print(f"❌ An error occurred: {e}")
