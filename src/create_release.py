import json
import os
import sys
import subprocess

def create_release(video_id):
    # 1. Locate the metadata file
    json_path = f"metadata/{video_id}.json"
    video_path = f"videos/{video_id}.mp4"

    if not os.path.exists(json_path):
        print(f"❌ Error: Metadata file not found at {json_path}")
        sys.exit(1)

    # 2. Load the JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    title = data.get("title", f"Video {video_id}")
    description = data.get("description", "No description provided.")
    pub_date = data.get("published_date", "Unknown Date")

    # 3. Format the Release Body
    release_body = f"""
## {title}
**Published Date:** {pub_date}
**Original URL:** {data.get('url')}

### Description
{description}
    """

    # 4. Use GitHub CLI to create the release
    # This is built-in to the GitHub runner and handles the upload
    print(f"🚀 Creating release for: {title}")
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"⚠️ Warning: Video file {video_path} not found. Creating release without asset.")
        asset_cmd = []
    else:
        asset_cmd = [video_path]

    try:
        subprocess.run([
            "gh", "release", "create", 
            video_id, 
            "--title", title, 
            "--notes", release_body,
        ] + asset_cmd, check=True)
        print("✅ Release created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create release: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_release.py <video_id>")
        sys.exit(1)
    
    create_release(sys.argv[1].strip())
