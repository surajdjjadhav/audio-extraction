import json
import os

def save_transcript_and_summary(video_title, transcript,summary, output_folder="downloads/json_files/"):
    """
    Saves video transcript and summary to a JSON file.
    Each video will be saved in a separate file named after the video title.
    """
    try:
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

        # Check if the file already exists, load it and append the new data
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        else:
            existing_data = []

        # Append new data
        existing_data.append(data)

        # Save the updated data back to the file
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, indent=4, ensure_ascii=False)

        print(f"✅ Transcript and summary saved to: {output_file}")
        return output_file

    except Exception as e:
        print(f"❌ Error saving transcript and summary: {e}")
        return None


# # Example usage
# if __name__ == "__main__":
#     output_file = save_transcript_and_summary()

