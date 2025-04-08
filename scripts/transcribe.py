import whisper
from indicnlp.normalize.indic_normalize import DevanagariNormalizer
import re
import os
import sys
import subprocess
import time
from transformers import pipeline
from scripts.logger import logging
from scripts.exception import MyException
from scripts.download_audio import download_audio
import warnings

warnings.filterwarnings("ignore")


def ensure_directory_exists(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        logging.info(f"Directory ensured: {directory}")
    except Exception as e:
        logging.error(f"Error creating directory {directory}: {e}")
        raise MyException(str(e), sys)


def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("FFmpeg is installed and available.")
    except FileNotFoundError:
        logging.error("FFmpeg is not installed or not added to PATH.")
        raise RuntimeError("FFmpeg is not installed or not added to PATH. Install it from https://ffmpeg.org/download.html")


class HindiTranscriber:
    def __init__(self, audio_file, model_size="base", summarizer_model="csebuetnlp/mT5_multilingual_XLSum"):
        check_ffmpeg()
        logging.info(f"Loading Whisper model '{model_size}'...")
        print(f"🔁 Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        logging.info("Whisper model loaded successfully.")
        print("✅ Whisper model loaded.")

        logging.info("Loading summarization model...")
        print("🔁 Loading summarization model...")
        self.summarizer = pipeline("summarization", model=summarizer_model, tokenizer=summarizer_model)
        logging.info("Summarization model loaded successfully.")
        print("✅ Summarization model loaded.")
        logging.info(f"Audio file path: {audio_file}")
        self.file_path = audio_file

    def transcribe_audio(self):
        try:
            if not os.path.exists(self.file_path):
                logging.error(f"Audio file not found: {self.file_path}")
                raise FileNotFoundError(f"Audio file not found: {self.file_path}")
            
            logging.info(f"Transcribing audio file: {self.file_path}")
            print("🔁 Transcribing audio... (this may take time on CPU)")

            start_time = time.time()
            result = self.model.transcribe(self.file_path, language="hi")
            duration = time.time() - start_time

            logging.info(f"Transcription completed in {duration:.2f} seconds.")
            print("✅ Transcription completed.")
            return result["text"]

        except KeyError as e:
            logging.error(f"Language 'hi' not supported: {e}")
            raise ValueError("The specified language 'hi' is not supported by the Whisper model.")
        except Exception as e:
            logging.error(f"Error during transcription: {e}")
            raise MyException(str(e), sys)

    def normalize_hindi_text(self, text):
        try:
            logging.info("Normalizing Hindi text...")
            print("🔁 Normalizing Hindi text...")
            normalizer = DevanagariNormalizer()
            normalized_text = normalizer.normalize(text)
            normalized_text = re.sub(r'\s+', ' ', normalized_text)
            normalized_text = re.sub(r'([।!?])', r' \1 ', normalized_text)
            logging.info("Text normalization complete.")
            print("✅ Normalization complete.")
            return normalized_text.strip()
        except Exception as e:
            logging.error(f"Normalization error: {e}")
            raise MyException(str(e), sys)

    def generate_summary(self, text, max_length=100, min_length=30):
        try:
            logging.info("Generating summary...")
            print("🔁 Generating summary...")

            word_count = len(text.split())
            logging.info(f"Text length: {word_count} words")

            if word_count < min_length:
                logging.warning("Text too short for summarization. Returning original text as summary.")
                return "Summary not generated: Transcription too short."

            summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            logging.info("Summary generation complete.")
            print("✅ Summary complete.")
            return summary[0]["summary_text"]
        except Exception as e:
            logging.error(f"Summary error: {e}")
            raise MyException(str(e), sys)

    def process_audio(self, output_dir):
        try:
            logging.info(f"Processing audio: {self.file_path}")
            ensure_directory_exists(output_dir)

            raw_text = self.transcribe_audio()
            clean_text = self.normalize_hindi_text(raw_text)
            summary = self.generate_summary(clean_text)

            base_name = os.path.basename(self.file_path).replace('.mp3', '.txt')
            output_path = os.path.join(output_dir, base_name)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Transcription:\n{clean_text}\n\nSummary:\n{summary}")

            logging.info(f"Output saved to: {output_path}")
            print(f"✅ Processing complete. Results saved to: {output_path}")
            return clean_text, summary

        except Exception as e:
            logging.error(f"Error in processing: {e}")
            raise MyException(str(e), sys)


if __name__ == "__main__":
    try:
        model_choice = input("🧠 Choose Whisper model size (tiny/base/small/medium/large): ").strip().lower()

        if model_choice not in ['tiny', 'base', 'small', 'medium', 'large']:
            print("⚠️ Invalid model selected. Using default: base")
            model_choice = "base"

        file_path = "downloads/raw_audio/suraj.mp3"

        transcriber = HindiTranscriber(audio_file=file_path, model_size=model_choice)
        transcriber.process_audio("downloads/transcribed_text")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
