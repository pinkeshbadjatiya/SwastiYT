import yt_dlp
import sys
import os
import re

def parse_issue_body(file_path):
    """
    Parses the issue body text file looking for sections delimited by #### key ####.
    Returns a dictionary of found keys and values.
    """
    if not os.path.exists(file_path):
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find blocks like #### key #### \n value
    # The pattern looks for #### (key) ####, then captures everything until the next #### or End of String
    pattern = r"####\s+(.+?)\s+####\s+(.*?)(?=(?:####)|$)"
    matches = re.findall(pattern, content, re.DOTALL)
    
    data = {}
    for key, value in matches:
        # Clean up whitespace
        clean_key = key.strip().lower()
        clean_value = value.strip()
        data[clean_key] = clean_value
    
    return data

def download_video(issue_data):
    # 1. Extract details from parsed data
    video_url = issue_data.get("url")
    video_id = issue_data.get("id")
    
    if not video_url:
        print("Error: 'url' field not found in issue description.")
        sys.exit(1)
        
    if not video_id:
        print("Warning: 'id' field not found. Will try to extract from URL or let yt-dlp decide.")
    
    # 2. Define output folder
    output_folder = os.path.join(os.getcwd(), "videos")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 3. Check if file already exists (Skip Logic)
    # We prefer using the ID from the issue body if available
    filename_id = video_id if video_id else "%(id)s"
    expected_filename = f"{filename_id}.mp4"
    expected_file_path = os.path.join(output_folder, expected_filename)
    
    if video_id and os.path.exists(expected_file_path):
        print(f"⏩ Skipping download: File already exists at {expected_file_path}")
        return

    # 4. Configure yt-dlp options
    ydl_opts = {
        # Use the ID from the issue as the filename
        'outtmpl': f'{output_folder}/{filename_id}.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    print(f"Starting download for URL: {video_url}")
    if video_id:
        print(f"Target Filename ID: {video_id}")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print("Download completed successfully.")
    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Expecting the file path of the issue body text as the first argument
    if len(sys.argv) > 1:
        issue_file_path = sys.argv[1]
        print(f"Parsing issue file: {issue_file_path}")
        
        parsed_data = parse_issue_body(issue_file_path)
        
        if parsed_data:
            print("Successfully parsed issue data.")
            download_video(parsed_data)
        else:
            print("Error: Could not read issue file or file is empty.")
            sys.exit(1)
    else:
        print("Error: No issue file path provided.")
        print("Usage: python download_video.py <path_to_issue_body.txt>")
        sys.exit(1)
