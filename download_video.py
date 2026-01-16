import yt_dlp
import sys
import os

def download_video(url):
    # Absolute path ensures we know exactly where files go on your machine
    # os.getcwd() gets the folder where the runner checked out the repo
    output_folder = os.path.join(os.getcwd(), "videos")
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ydl_opts = {
        'outtmpl': f'{output_folder}/%(id)s.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': True,
        # On a self-hosted runner (Residential IP), you rarely need cookies!
        # But we keep a standard user agent just in case.
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
