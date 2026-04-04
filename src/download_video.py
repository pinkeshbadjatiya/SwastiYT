import yt_dlp
import sys
import os
import re
import json
import argparse
from helpers import reorder_entries_of_yt_with_oldest_first

# Global channel configuration
CHANNEL_ID = "UCx9PzFr70x2194NbRB9JpQw"
SOURCE_URL = f"https://www.youtube.com/channel/{CHANNEL_ID}/videos"

# Languages to download subtitles for (to avoid rate limits)
# Added Telugu (te) and Tamil (ta)
LANGS_TO_DOWNLOAD = ['en', 'hi', 'es', 'te', 'ta']

VIDEOS_FOLDER = "videos"
METADATA_FOLDER = "metadata"

def parse_issue_content(content):
    """
    Parses a raw issue string or direct video payload.
    """
    if not content:
        return None

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


def playlist_video_ids():
    global SOURCE_URL

    print(f"Fetching video list from source: {SOURCE_URL}")
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'skip_download': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(SOURCE_URL, download=False)
    except Exception as e:
        print(f"Error fetching list from source URL: {e}")
        return []

    entries = info.get('entries') if isinstance(info, dict) else None
    if not entries:
        video_id = info.get('id') if isinstance(info, dict) else None
        return [video_id] if video_id else []

    # Reorder entries to ensure oldest videos are first, so that we download the oldest first
    entries = reorder_entries_of_yt_with_oldest_first(entries)

    video_ids = []
    for entry in entries:
        if not entry:
            continue
        vid = entry.get('id') or entry.get('url') or entry.get('webpage_url')
        if vid:
            video_ids.append(vid)
    return video_ids


def is_video_downloaded(video_id):
    """
    Checks if a video with the given ID has already been downloaded by looking for MP4 files in the expected directory.
    """
    global VIDEOS_FOLDER

    if not video_id:
        return False

    video_dir = os.path.join(os.getcwd(), VIDEOS_FOLDER, video_id)
    if not os.path.isdir(video_dir):
        return False

    for filename in os.listdir(video_dir):
        if filename.lower().endswith('.mp4'):
            return True
    return False


def find_next_pending_video():
    # Get all video IDs from the source playlist
    video_ids = playlist_video_ids()
    if not video_ids:
        print("No videos found in source list.")
        return None

    # Check each video ID against the local videos folder to see if it's already downloaded
    for video_id in video_ids:
        if not is_video_downloaded(video_id):
            print(f"Found pending video_id: {video_id}")
            return video_id

    print("All videos from source are already downloaded.")
    return None


def get_task_args():
    parser = argparse.ArgumentParser(description="Download YouTube videos by task mode")
    parser.add_argument("--task", choices=["single_video", "next_video"], required=True,
                        help="Task type to execute")
    parser.add_argument("--video_id", default=None,
                        help="Video ID or URL for single_video task")
    return parser.parse_args()


def main():
    args = get_task_args()

    if args.task == "single_video":
        if not args.video_id:
            print("Error: --video_id is required for --task=single_video")
            sys.exit(1)

        parsed_data = parse_issue_content(args.video_id)
        if not parsed_data:
            print("Error parsing video ID or URL provided for single_video task.")
            sys.exit(1)

    elif args.task == "next_video":
        pending_video_id = find_next_pending_video()
        if not pending_video_id:
            print("Error: No pending video found for next_video task.")
            sys.exit(1)

        parsed_data = parse_issue_content(pending_video_id)
        if not parsed_data:
            print(f"Error parsing pending video ID: {pending_video_id}")
            sys.exit(1)

    # Download the video using the parsed data (either from single_video or next_video)
    download_video(parsed_data)


def save_metadata(data, video_id, lang):
    global METADATA_FOLDER
    # Extract fields from yt-dlp's info_dict
    title = data.get("title", "No Title Found")
    url = data.get("webpage_url", "")  # yt-dlp uses 'webpage_url', not 'url'
    published_date = data.get("upload_date", "")  # Format: YYYYMMDD
    
    # Handle thumbnails - yt-dlp provides both 'thumbnail' (best) and 'thumbnails' (list)
    thumbnail = data.get("thumbnail", "")
    if not thumbnail and data.get("thumbnails"):
        thumbnail = data["thumbnails"][-1].get("url", "")  # Get highest res thumbnail
    
    duration = data.get("duration", 0)  # In seconds
    description = data.get("description", "")
    subtitles = data.get("subtitles", {})
    tags = data.get("tags", [])
    
    # Additional useful fields from yt-dlp
    uploader = data.get("uploader", "")
    uploader_id = data.get("uploader_id", "")
    channel = data.get("channel", "")
    view_count = data.get("view_count", 0)
    like_count = data.get("like_count", 0)
    comment_count = data.get("comment_count", 0)

    # Check for localized title and description
    localizations = data.get("localizations", {})
    if lang in localizations:
        loc = localizations[lang]
        title = loc.get("title", title)
        description = loc.get("description", description)

    if not video_id:
        print("Error: Video ID missing in issue data.")
        return

    # Create a simplified metadata dictionary with only the required fields.
    # Keep tags/common info shared, and store title/description per language.
    simplified_metadata = {
        "id": video_id,
        "url": url,
        "published_date": published_date,
        "thumbnail": thumbnail,
        "duration": duration,
        "tags": tags,
        "uploader": uploader,
        "uploader_id": uploader_id,
        "channel": channel,
        "view_count": view_count,
        "like_count": like_count,
        "comment_count": comment_count,
        "language": lang,
        "title": title,
        "description": description,
    }

    # Save JSON Metadata for the specific language
    json_path = os.path.join(METADATA_FOLDER, f"{video_id}", f"{lang}.json")
    try:
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(simplified_metadata, f, indent=4)
        print(f"Metadata saved: {json_path}")
    except Exception as e:
        print(f"Error saving metadata: {e}")

def download_video(issue_data):
    # Extract video URL/ID from issue to know what to download
    video_url = issue_data.get("url")
    
    if not video_url:
        print("Error: 'url' field not found.")
        sys.exit(1)

    base_dir = os.getcwd()
    videos_folder = os.path.join(base_dir, "videos")
    metadata_folder = os.path.join(base_dir, "metadata")

    for folder in [videos_folder, metadata_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Extract metadata from yt-dlp first (before downloading)
    print(f"Extracting metadata from yt-dlp for: {video_url}")
    try:
        extraction_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,  # Get full info, not just flat
        }
        with yt_dlp.YoutubeDL(extraction_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            video_id = info_dict.get("id")
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        sys.exit(1)

    if not video_id:
        print("Error: Could not extract video ID from yt-dlp.")
        sys.exit(1)

    # Get list of available audio languages
    formats = info_dict.get('formats', [])
    audio_langs = set()
    for fmt in formats:
        if fmt.get('acodec') != 'none' and fmt.get('language'):
            audio_langs.add(fmt['language'])
    if not audio_langs:
        audio_langs = {'en'}  # Default to English if no languages detected

    print(f"Detected audio languages: {', '.join(audio_langs)}")

    # Determine available audio languages from formats
    formats = info_dict.get('formats', [])
    available_audio_langs = set()
    for fmt in formats:
        if fmt.get('acodec') != 'none' and fmt.get('language'):
            available_audio_langs.add(fmt['language'])

    target_langs = [l for l in LANGS_TO_DOWNLOAD]

    def find_matching_audio_lang(target, available_langs):
        if target in available_langs:
            return target
        for avail in available_langs:
            if avail.split('-')[0] == target:
                return avail
        return None

    # Check existence - if any lang.mp4 exists, skip
    expected_video_dir = os.path.join(VIDEOS_FOLDER, video_id)
    if os.path.exists(expected_video_dir):
        mp4_files = [f for f in os.listdir(expected_video_dir) if f.lower().endswith('.mp4') and not f.startswith('video')]
        if mp4_files:
            print(f"⏩ Skipping download: Video directory already contains language MP4 files: {expected_video_dir}")
            return

    # We'll download per-language merged files (video+audio) directly as <lang>.mp4
    video_format = 'bestvideo[ext=mp4]'

    # Download audio for each target language and merge with video
    for lang in target_langs:
        matching_lang = find_matching_audio_lang(lang, available_audio_langs)
        if not matching_lang:
            print(f"No audio stream for {lang}; skipping creation of {lang}.mp4")
            continue

        if matching_lang != lang:
            print(f"Falling back from requested language '{lang}' to available audio language '{matching_lang}'")

        audio_format = f'bestaudio[language={matching_lang}]'
        merge_opts = {
            'outtmpl': f'{VIDEOS_FOLDER}/{video_id}/{lang}.mp4',
            'format': f'{video_format}+{audio_format}',
            'merge_output_format': 'mp4',
            'quiet': False,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            # Do not save subtitles, thumbnails, infojson, annotations or descriptions
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        print(f"Downloading and merging audio for language: {lang} (using {matching_lang})")
        try:
            with yt_dlp.YoutubeDL(merge_opts) as ydl:
                ydl.download([video_url])
            save_metadata(info_dict, video_id, lang)
        except Exception as e:
            print(f"Error downloading for language {lang}: {e}")
            continue
    
    print("Download success for all languages.")


if __name__ == "__main__":
    main()

