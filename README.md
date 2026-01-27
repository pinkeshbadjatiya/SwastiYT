# SwastiYT

This repository facilitates the automated download and distribution of YouTube videos based on GitHub Issues.

## Project Restructuring and Task Management

To better track the stages of video processing, a comprehensive task management system has been implemented:

### Task Status Tracking

Video task statuses are now managed in [task-status.json](task-status.json). This file uses the video ID as a key, with values representing the status of various tasks (e.g., `download_video`, `publish_video`). Workflows check dependencies in this file before executing a task and update the status upon completion.

### Workflows

#### 1. Download Video Task ([.github/workflows/download_video_task.yml](.github/workflows/download_video_task.yml))

This workflow is triggered when a new GitHub Issue with a title starting with 'Download' is opened. Its primary responsibilities include:

- Setting up a Python virtual environment and installing `yt-dlp`.
- Parsing the issue body to extract video information (URL, ID).
- Downloading the video, all available language audio tracks, subtitles, and metadata.
- Organizing the downloaded content into `videos/<video_id>/<lang>.mp4` for video files and `videos/<video_id>/<lang>.json` for metadata (including subtitles and tags).
- Committing and pushing the new video and metadata files to the repository.
- Updating the `download_video` task status in [task-status.json](task-status.json) to `completed`.
- Closing the GitHub issue upon successful download.

#### 2. Release Video Task ([.github/workflows/release_video_task.yml](.github/workflows/release_video_task.yml))

This workflow is designed to release videos for distribution (e.g., to Zapier). It is triggered manually or can be set up to run on a schedule (e.g., every 12 hours) and performs the following:

- Checks [task-status.json](task-status.json) to find videos where the `download_video` task is `completed` and the `publish_video` task is `pending`.
- Processes one video at a time.
- Reads the metadata (title, etc.) from the corresponding `videos/<video_id>/en.json` file.
- Creates a GitHub Release with the video ID as the tag name and the video title as the release name.
- Attaches the main video file (`videos/<video_id>/en.mp4`) to the release.
- Updates the `publish_video` task status in [task-status.json](task-status.json) to `completed`.

### Source Code Structure

All Python source code files have been moved into the `src/` directory for better organization:

- `src/download_video.py`: The main script for downloading YouTube videos.
- `src/update_task_status.py`: A utility script to update task statuses in [task-status.json](task-status.json).

### Task Configuration

Task keys and their dependencies are defined in [task_config.yml](task_config.yml) at the root of the repository. This file outlines the sequence and relationships between different video processing tasks.
