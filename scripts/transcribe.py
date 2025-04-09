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
import torch 

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

        # Automatically detect GPU
        if torch.cuda.is_available():
            self.device = "cuda"
            self.device_id = 0
        else:
            self.device = "cpu"
            self.device_id = -1

        self.model_size = model_size
        self.file_path = audio_file

        self._log_gpu_memory_info()

        logging.info(f"Loading Whisper model '{self.model_size}' on {self.device}...")
        print(f"🔁 Loading Whisper model: {self.model_size} on {self.device}")
        try:
            self.model = whisper.load_model(self.model_size, device=self.device)
        except RuntimeError as e:
            logging.error(f"Failed to load Whisper model: {e}")
            raise MyException(str(e), sys)

        logging.info("Whisper model loaded successfully.")
        print("✅ Whisper model loaded.")

        logging.info("Loading summarization model...")
        print("🔁 Loading summarization model...")

        # GPU memory check before summarizer
        if self.device == "cuda" and self.get_free_gpu_memory() < 3000:
            logging.warning("Not enough GPU memory for summarizer, switching to CPU.")
            self.device_id = -1

        try:
            self.summarizer = pipeline(
                "summarization",
                model=summarizer_model,
                tokenizer=summarizer_model,
                device=self.device_id
            )
        except Exception as e:
            if self.device_id == 0:
                logging.warning("Retrying summarizer on CPU...")
                try:
                    self.summarizer = pipeline(
                        "summarization",
                        model=summarizer_model,
                        tokenizer=summarizer_model,
                        device=-1
                    )
                    logging.info("Summarizer loaded on CPU.")
                except Exception as ex:
                    logging.error(f"Summarization model failed on both GPU and CPU: {ex}")
                    raise MyException(str(ex), sys)
            else:
                logging.error(f"Failed to load summarization model: {e}")
                raise MyException(str(e), sys)

        logging.info("Summarization model loaded successfully.")
        print("✅ Summarization model loaded.")

    def get_free_gpu_memory(self):
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,nounits,noheader"],
                stdout=subprocess.PIPE, text=True
            )
            mem = int(result.stdout.strip().split('\n')[0])
            return mem
        except Exception as e:
            logging.warning("Unable to get GPU memory info. Assuming low memory.")
            return -1

    def _log_gpu_memory_info(self):
        if self.device == "cuda":
            try:
                total = torch.cuda.get_device_properties(0).total_memory // (1024 ** 2)
                allocated = torch.cuda.memory_allocated(0) // (1024 ** 2)
                logging.info(f"GPU memory: Total = {total} MB, Allocated = {allocated} MB")
            except Exception as e:
                logging.warning(f"Failed to log GPU memory info: {e}")
    def process_audio(self, output_dir):
        try:
            ensure_directory_exists(output_dir)

            logging.info(f"Transcribing audio file: {self.file_path}")
            print("🔁 Transcribing audio...")

            # Run the transcription
            result = self.model.transcribe(self.file_path, language="hi")

            # Normalize text
            text = result["text"]
            normalizer = DevanagariNormalizer()
            normalized_text = normalizer.normalize(text)

            logging.info("Transcription complete.")
            print("✅ Transcription complete.")

            logging.info("Generating summary...")
            print("🔁 Generating summary...")
            summary_result = self.summarizer(normalized_text, max_length=100, min_length=30, do_sample=False)
            summary = summary_result[0]["summary_text"]

            logging.info("Summary generation complete.")
            print("✅ Summary generation complete.")

            return normalized_text, summary

        except Exception as e:
            logging.error(f"Error in process_audio: {e}")
            raise MyException(str(e), sys)



# if __name__ == "__main__":
#     try:
#         model_choice = input("🧠 Choose Whisper model size (tiny/base/small/medium/large): ").strip().lower()

#         if model_choice not in ['tiny', 'base', 'small', 'medium', 'large']:
#             print("⚠️ Invalid model selected. Using default: base")
#             model_choice = "base"

#         file_path = "downloads/raw_audio/suraj.mp3"

#         transcriber = HindiTranscriber(audio_file=file_path, model_size=model_choice)
#         transcriber.process_audio("downloads/transcribed_text")

#     except Exception as e:
#         print(f"❌ An error occurred: {e}")
