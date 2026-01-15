import yt_dlp
import sys
import os

def download_video(url):
    # 1. Create the output folder if it doesn't exist
    output_folder = "videos"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 2. Configure yt-dlp options
    ydl_opts = {
        # Save file as: videos/<video-id>.mp4
        'outtmpl': f'{output_folder}/%(id)s.%(ext)s',
        
        # Format: Best MP4 video + Best M4A audio, OR best mp4 available
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        
        # Ensure final container is mp4
        'merge_output_format': 'mp4',
        
        # Reduce terminal clutter, but keep errors visible
        'quiet': False,
        'no_warnings': True,
        
        # OPTIONAL: Use a browser User-Agent to further reduce bot detection risks
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    print(f"Starting download for URL: {url}")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download completed successfully.")
    except Exception as e:
        print(f"Critical Error: {e}")
        # Exit with error code so the GitHub Action knows it failed
        sys.exit(1)

if __name__ == "__main__":
    # 3. Read the URL from command line arguments
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
        download_video(video_url)
    else:
        print("Error: No URL provided.")
        print("Usage: python download_video.py <URL>")
        sys.exit(1)
