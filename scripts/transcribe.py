import whisper

def transcribe_audio(audio_path):
    model = whisper.load_model("base")  # 'base', 'small', 'medium', 'large'
    result = model.transcribe(audio_path)
    return result["text"]

if __name__ == "__main__":
    text = transcribe_audio("downloads/audio.mp3")
    print("Transcription:\n", text)
