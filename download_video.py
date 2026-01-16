import yt_dlp
import sys
import os

def get_video_id(url):
    """
    Extracts the YouTube Video ID from the URL.
    Assumes URL format: https://www.youtube.com/watch?v=<ID>
    """
    try:
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
    except Exception:
        pass
    return None

def download_video(url):
    # 1. Define output folder
    # os.getcwd() is safer on self-hosted runners to ensure absolute paths
    output_folder = os.path.join(os.getcwd(), "videos")
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 2. SKIP LOGIC: Check if file already exists
    video_id = get_video_id(url)
    if video_id:
        expected_file = os.path.join(output_folder, f"{video_id}.mp4")
        if os.path.exists(expected_file):
            print(f"⏩ Skipping download: File already exists at {expected_file}")
            return
    else:
        print("Warning: Could not extract Video ID from URL. Proceeding with download attempt...")

    # 3. Configure yt-dlp options
    ydl_opts = {
        'outtmpl': f'{output_folder}/%(id)s.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': True,
        # 'no_overwrites': True, # Redundant given our manual check, but good backup
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    print(f"Starting download for URL: {url}")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download completed successfully.")
    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
        download_video(video_url)
    else:
        print("Error: No URL provided.")
        sys.exit(1)
