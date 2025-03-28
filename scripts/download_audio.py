import yt_dlp

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

if __name__ == "__main__":
    video_url = input("Enter YouTube video URL: ")
    audio_file = download_audio(video_url)
    print(f"Downloaded audio: {audio_file}")
