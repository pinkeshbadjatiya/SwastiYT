import youtube_dl
import sys
import os

def download_video(url):
    # 1. Create the output folder if it doesn't exist
    output_folder = "videos"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 2. Configure youtube-dl options
    ydl_opts = {
        # Save file as: videos/<video-id>.mp4
        'outtmpl': f'{output_folder}/%(id)s.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'no_warnings': True,
    }

    print(f"Starting download for URL: {url}")

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download completed successfully.")
    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 3. Read the URL from command line arguments
    if len(sys.argv) > 1:
        # Assign the argument to the variable explicitly
        video_url = sys.argv[1]
        download_video(video_url)
    else:
        print("Error: No URL provided.")
        print("Usage: python download_video.py <URL>")
        sys.exit(1)
