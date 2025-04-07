import whisper
from indicnlp.normalize.indic_normalize import DevanagariNormalizer
import re
import os
import sys
import subprocess
from transformers import pipeline
from scripts.logger import logging
from scripts.exception import MyException

def ensure_directory_exists(directory):
    """Ensure the given directory exists."""
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        logging.info(f"Directory ensured: {directory}")
    except Exception as e:
        logging.error(f"Error creating directory {directory}: {e}")
        raise MyException(str(e), sys)

def check_ffmpeg():
    """Check if FFmpeg is installed and available."""
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("FFmpeg is installed and available.")
    except FileNotFoundError:
        logging.error("FFmpeg is not installed or not added to PATH.")
        raise RuntimeError("FFmpeg is not installed or not added to PATH. Install it from https://ffmpeg.org/download.html")

class HindiTranscriber:
    def __init__(self, model_size="medium", summarizer_model="facebook/bart-large-cnn"):
        """
        Initialize the transcription class with a Whisper model and a summarization model.
        """
        check_ffmpeg()  # Ensure FFmpeg is available
        logging.info("Loading Whisper model...")
        self.model = whisper.load_model(model_size)
        logging.info("Whisper model loaded successfully.")
        logging.info("Loading summarization model...")
        self.summarizer = pipeline("summarization", model=summarizer_model)
        logging.info("Summarization model loaded successfully.")

    def transcribe_audio(self, audio_file):
        """
        Transcribes an audio file and returns the raw Hindi text.
        """
        try:
            audio_file = f"{audio_file}"
            if not os.path.exists(audio_file):
                logging.error(f"Audio file not found: {audio_file}")
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
            logging.info(f"Transcribing audio file: {audio_file}")
            result = self.model.transcribe(audio_file, language="hi")
            logging.info("Transcription completed successfully.")
            return result["text"]
        except KeyError as e:
            logging.error(f"Error in transcription: Language 'hi' might not be supported. {e}")
            raise ValueError("The specified language 'hi' is not supported by the Whisper model.")
        except Exception as e:
            logging.error(f"Error in transcribing audio: {e}")
            raise MyException(str(e), sys)

    def normalize_hindi_text(self, text):
        """
        Normalizes Devanagari script to remove inconsistencies and fix spacing.
        """
        try:
            logging.info("Normalizing Hindi text...")
            if not hasattr(DevanagariNormalizer, "normalize"):
                logging.error("DevanagariNormalizer is not properly initialized.")
                raise ImportError("DevanagariNormalizer is not available. Check the indic-nlp-library installation.")
            
            normalizer = DevanagariNormalizer()
            normalized_text = normalizer.normalize(text)
            
            # Fix spacing and punctuation issues
            normalized_text = re.sub(r'\s+', ' ', normalized_text)  # Remove extra spaces
            normalized_text = re.sub(r'([।!?])', r' \1 ', normalized_text)  # Space out punctuation
            
            logging.info("Text normalization completed successfully.")
            return normalized_text.strip()
        except Exception as e:
            logging.error(f"Error in normalizing text: {e}")
            raise MyException(str(e), sys)

    def generate_summary(self, text, max_length=100, min_length=30):
        """
        Generates a summary from the given text.
        """
        try:
            logging.info("Generating summary...")
            if not hasattr(self.summarizer, "__call__"):
                logging.error("Summarization model is not properly initialized.")
                raise RuntimeError("Summarization model is not available. Check the transformers library installation.")
            
            summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            logging.info("Summary generated successfully.")
            return summary[0]["summary_text"]
        except Exception as e:
            logging.error(f"Error in generating summary: {e}")
            raise MyException(str(e), sys)

    def process_audio(self, audio_path, output_dir):
        """
        Transcribes, normalizes, and generates a summary from an audio file.
        Saves the results in a text file.
        """
        try:
            logging.info(f"Processing audio file: {audio_path}")
            ensure_directory_exists(output_dir)
            raw_text = self.transcribe_audio(audio_path)
            clean_text = self.normalize_hindi_text(raw_text)
            summary = self.generate_summary(clean_text)

            # Save results
            base_name = os.path.basename(audio_path).replace('.mp3', '.txt')
            output_path = os.path.join(output_dir, base_name)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Transcription:\n{clean_text}\n\nSummary:\n{summary}")
            
            logging.info(f"Processing complete! Output saved at: {output_path}")
            return clean_text, summary
        except Exception as e:
            logging.error(f"Error in processing audio: {e}")
            raise MyException(str(e), sys)