import yt_dlp
import sys
import os
import re
import json

def parse_issue_body(file_path):
    if not os.path.exists(file_path):
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find blocks like #### key #### \n value
    pattern = r"####\s+(.+?)\s+####\s+(.*?)(?=(?:####)|$)"
    matches = re.findall(pattern, content, re.DOTALL)
    
    data = {}
    for key, value in matches:
        clean_key = key.strip().lower()
        clean_value = value.strip()
        data[clean_key] = clean_value
    
    return data

def save_metadata(data, folder):
    video_id = data.get("id")
    title = data.get("title", "No Title Found")
    description = data.get("description", "")

    if not video_id:
        print("Error: Video ID missing in issue data.")
        return

    # 1. Save JSON Metadata for record-keeping
    json_path = os.path.join(folder, f"{video_id}.json")
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Metadata saved: {json_path}")
    except Exception as e:
        print(f"Error saving metadata: {e}")

    # 2. Save individual text files for GitHub Workflow/Zapier access
    files_to_create = {
        "video_id.txt": video_id,
        "video_title.txt": title,
        "video_description.txt": description,
        "release_body.txt": f"{title}\n\n{description}" # Used for Instagram Body
    }

    for filename, content in files_to_create.items():
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created {filename}")
        except Exception as e:
            print(f"Error saving {filename}: {e}")

def download_video(issue_data):
    video_url = issue_data.get("url")
    video_id = issue_data.get("id")
    
    if not video_url:
        print("Error: 'url' field not found.")
        sys.exit(1)

    base_dir = os.getcwd()
    videos_folder = os.path.join(base_dir, "videos")
    metadata_folder = os.path.join(base_dir, "metadata")

    for folder in [videos_folder, metadata_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Save all helper files (ID, Title, Description, etc.)
    save_metadata(issue_data, metadata_folder)

    # Check existence
    filename_id = video_id if video_id else "%(id)s"
    expected_file_path = os.path.join(videos_folder, f"{filename_id}.mp4")
    
    if video_id and os.path.exists(expected_file_path):
        print(f"⏩ Skipping download: File exists at {expected_file_path}")
        return

    # Download
    ydl_opts = {
        'outtmpl': f'{videos_folder}/{filename_id}.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    print(f"Starting download: {video_url}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print("Download success.")
    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        issue_file_path = sys.argv[1]
        parsed_data = parse_issue_body(issue_file_path)
        if parsed_data:
            download_video(parsed_data)
        else:
            print("Error parsing issue file.")
            sys.exit(1)
    else:
        print("Error: No file path provided.")
        sys.exit(1)
