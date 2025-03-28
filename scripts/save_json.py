import json
import os
from transformers import pipeline

# Load Summarization Model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(full_text):
    summary = summarizer(full_text, max_length=100, min_length=50, do_sample=False)
    return summary[0]['summary_text']

def save_transcription(video_title, transcript, json_file="downloads/movie.json"):
    os.makedirs("downloads", exist_ok=True)  # Ensure downloads folder exists

    # Generate summary
    summary = summarize_text(transcript)

    # Load existing data
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Append new entry
    data.append({"title": video_title, "description": summary, "script": transcript})

    # Save to JSON file
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    return summary

if __name__ == "__main__":
    sample_title = "Example Video"
    sample_transcript = "This is a sample transcript of the video."

    summary = save_transcription(sample_title, sample_transcript)
    print("\nSummary (3-Line Description):\n", summary)
    print("Saved transcript to JSON!")
