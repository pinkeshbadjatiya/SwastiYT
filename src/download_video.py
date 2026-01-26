import yt_dlp
import sys
import os
import re
import json

def parse_issue_body(file_path):
    """
    Parses the issue body file.
    1. First attempts to let yt-dlp extract info directly (works for raw URLs and IDs).
    2. Falls back to Regex if the body uses the structured #### format.
    """
    if not os.path.exists(file_path):
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        # strip() is crucial to remove accidental newlines from the issue body
        content = f.read().strip()

    print(f"Parsing content: {content}")

    # --- STRATEGY 1: Direct yt-dlp Extraction (Smartest Method) ---
    try:
        ydl_opts = {
            'quiet': True, 
            'no_warnings': True,
            # We use extract_flat to get metadata fast without downloading yet
            'extract_flat': True 
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # This works if 'content' is a URL OR a Video ID
            info = ydl.extract_info(content, download=False)
            
            # If input was just an ID, yt-dlp might not give a full URL, so we construct it
            video_url = info.get("webpage_url")
            if not video_url:
                video_url = f"https://www.youtube.com/watch?v={info.get('id')}"

            print("✅ Successfully parsed via yt-dlp.")
            return {
                "id": info.get("id"),
                "url": video_url,
                "title": info.get("title"),
                "description": info.get("description")
            }
    except Exception as e:
        print(f"⚠️ yt-dlp extraction failed (valid if input is structured text), trying regex fallback: {e}")

    # --- STRATEGY 2: Regex Fallback (For structured inputs) ---
    # Regex to find blocks like #### key #### \n value
    pattern = r"####\s+(.+?)\s+####\s+(.*?)(?=(?:####)|$)"
    matches = re.findall(pattern, content, re.DOTALL)
    
    if matches:
        data = {}
        for key, value in matches:
            clean_key = key.strip().lower()
            clean_value = value.strip()
            data[clean_key] = clean_value
        print("✅ Successfully parsed via Regex.")
        return data
    
    return None

def save_metadata(data, metadata_folder, video_id, lang):
    title = data.get("title", "No Title Found")
    url = data.get("url", "")
    published_date = data.get("upload_date", "")
    thumbnail = data.get("thumbnail", "")
    duration = data.get("duration", "")
    description = data.get("description", "")
    subtitles = data.get("subtitles", {})
    tags = data.get("tags", [])

    if not video_id:
        print("Error: Video ID missing in issue data.")
        return

    # Create a simplified metadata dictionary with only the required fields
    simplified_metadata = {
        "id": video_id,
        "title": title,
        "url": url,
        "published_date": published_date,
        "thumbnail": thumbnail,
        "duration": duration,
        "description": description,
        "subtitles": subtitles,
        "tags": tags
    }

    # Save JSON Metadata for the specific language
    json_path = os.path.join(metadata_folder, f"{video_id}", f"{lang}.json")
    try:
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(simplified_metadata, f, indent=4)
        print(f"Metadata saved: {json_path}")
    except Exception as e:
        print(f"Error saving metadata: {e}")

    # Save individual text files for GitHub Workflow/Zapier access
    # These are saved in the ROOT directory so the workflow can find them easily
    files_to_create = {
        "video_id.txt": video_id,
        "video_title.txt": title,
        "video_description.txt": description,
        "release_body.txt": f"{title}\n\n{description}" # Used for Instagram Body
    }

    for filename, content in files_to_create.items():
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(str(content))
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
    save_metadata(issue_data, metadata_folder, video_id, "en")

    # Check existence
    filename_id = video_id if video_id else "%(id)s"
    expected_file_path = os.path.join(videos_folder, f"{filename_id}.mp4")
    
    if video_id and os.path.exists(expected_file_path):
        print(f"⏩ Skipping download: File exists at {expected_file_path}")
        return

    # Download all language audio tracks and organize them in folders by language ID
    ydl_opts = {
        'outtmpl': {
            'default': f'{videos_folder}/{filename_id}/%(lang)s.%(ext)s',
            'infojson': f'{videos_folder}/{filename_id}/%(lang)s.json',
        },
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['all'],
        'subtitlesformat': 'vtt',
        'writethumbnail': True,
        'writeinfojson': True,
        'writeannotations': True,
        'writedescription': True,
        'writeallsubs': True,
        'allsubtitles': True,
    }

    print(f"Starting download: {video_url}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            
            # Extract subtitles from the info_dict and save them to the metadata
            subtitles = info_dict.get("subtitles", {})
            if subtitles:
                for lang, subtitle_info in subtitles.items():
                    save_metadata(info_dict, metadata_folder, video_id, lang)
            else:
                save_metadata(info_dict, metadata_folder, video_id, "en")
        
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