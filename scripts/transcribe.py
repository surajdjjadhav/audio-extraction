import whisper
from indicnlp.normalize.indic_normalize import DevanagariNormalizer
import re
import os
from transformers import pipeline
import sys

def ensure_directory_exists(directory):
    """Ensure the given directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)

class HindiTranscriber:
    def __init__(self, model_size="medium", summarizer_model="facebook/bart-large-cnn"):
        """
        Initialize the transcription class with a Whisper model and a summarization model.
        """
        self.model = whisper.load_model(model_size)
        self.summarizer = pipeline("summarization", model=summarizer_model)

    def transcribe_audio(self, audio_file):
        """
        Transcribes an audio file and returns the raw Hindi text.
        """
        result = self.model.transcribe(audio_file, language="hi")
        return result["text"]

    def normalize_hindi_text(self, text):
        """
        Normalizes Devanagari script to remove inconsistencies and fix spacing.
        """
        normalizer = DevanagariNormalizer()
        normalized_text = normalizer.normalize(text)
        
        # Fix spacing and punctuation issues
        normalized_text = re.sub(r'\s+', ' ', normalized_text)  # Remove extra spaces
        normalized_text = re.sub(r'([।!?])', r' \1 ', normalized_text)  # Space out punctuation
        
        return normalized_text.strip()

    def generate_summary(self, text, max_length=100, min_length=30):
        """
        Generates a summary from the given text.
        """
        summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]["summary_text"]

    def process_audio(self, audio_path, output_dir):
        """
        Transcribes, normalizes, and generates a summary from an audio file.
        Returns the transcribed text and its summary.
        """
        ensure_directory_exists(output_dir)
        
        raw_text = self.transcribe_audio(audio_path)
        clean_text = self.normalize_hindi_text(raw_text)
        summary = self.generate_summary(clean_text)

        # Save results
        base_name = os.path.basename(audio_path).replace('.mp3', '.txt')
        with open(os.path.join(output_dir, base_name), 'w', encoding='utf-8') as f:
            f.write(f"Transcription:\n{clean_text}\n\nSummary:\n{summary}")
        
        return clean_text, summary

# # Example Usage:
# if __name__ == "__main__":

#     transcriber = HindiTranscriber(model_size="medium")  # Initialize
    
