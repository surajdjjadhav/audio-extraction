import os

# Define project structure
project_name = "youtube_audio_transcriber"
directories = [
    "downloads",
    "models",
    "scripts"
]
files = {
    "scripts/download_audio.py": """import yt_dlp

def download_audio(youtube_url, output_path="downloads/audio.mp3"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    return output_path
""",
    
    "scripts/transcribe.py": """import whisper

def transcribe_audio(audio_path):
    model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
    result = model.transcribe(audio_path)
    return result["text"]
""",
    
    "app.py": """import streamlit as st
from scripts.download_audio import download_audio
from scripts.transcribe import transcribe_audio

st.title("🎥 YouTube Video to Text AI")

video_url = st.text_input("Enter YouTube Video URL:")
if st.button("Convert to Text"):
    if video_url:
        st.write("🔄 Downloading Audio...")
        audio_path = download_audio(video_url)

        st.write("🎙️ Transcribing Audio...")
        transcript = transcribe_audio(audio_path)

        st.write("✅ Transcription Complete!")
        st.text_area("Transcribed Text:", transcript, height=300)
    else:
        st.warning("⚠️ Please enter a valid YouTube URL.")
""",
    
    "requirements.txt": "yt-dlp\nopenai-whisper\ntorch\nstreamlit\nmoviepy\n",
    
    "README.md": "# YouTube Video to Text AI\nThis project extracts audio from YouTube videos and converts them to text using Whisper AI."
}

# Create directories
for directory in directories:
    os.makedirs(os.path.join(project_name, directory), exist_ok=True)

# Create files with initial content
for file_path, content in files.items():
    full_path = os.path.join(project_name, file_path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"✅ Project '{project_name}' created successfully!")
