import streamlit as st
import os
import json
from scripts.download_audio import download_audio
from scripts.transcribe import transcribe_audio
from scripts.save_json import save_transcription

st.title("🎥 YouTube Video Script Generator ✍️")

video_title = st.text_input("Enter Video Title:")
video_url = st.text_input("Enter YouTube Video Link:")

if st.button("Generate Script"):
    if video_title and video_url:
        st.write("📥 Downloading Audio...")
        audio_path = download_audio(video_url)

        st.write("🎙️ Extracting & Transcribing Audio...")
        transcript = transcribe_audio(audio_path)

        st.write("💾 Saving Transcript & Creating Summary...")
        summary = save_transcription(video_title, transcript)

        st.success("Script and Summary Saved!")
        st.write("📄 **Summary:**", summary)
        st.write("📜 **Full Script:**", transcript)
    else:
        st.warning("⚠️ Please enter both Video Title and Video Link!")

# Display all saved stories
st.subheader("📚 Saved Stories")
if os.path.exists("downloads/movie.json"):
    with open("downloads/movie.json", "r", encoding="utf-8") as file:
        stories = json.load(file)
        for story in stories:
            st.write(f"**🎬 Title:** {story['title']}")
            st.write(f"📄 **Description:** {story['description']}")
            st.write("---")
