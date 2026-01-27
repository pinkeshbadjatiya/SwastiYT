import json
import sys
import os

def update_task_status(video_id, task_key, status):
    pending_tasks_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tasks", "pending.json")

    if not os.path.exists(pending_tasks_file):
        print(f"Error: {pending_tasks_file} not found.")
        sys.exit(1)

    try:
        with open(pending_tasks_file, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            
            if video_id in data:
                if task_key in data[video_id]:
                    data[video_id][task_key] = status
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    print(f"Successfully updated task '{task_key}' for video '{video_id}' to '{status}'.")
                else:
                    print(f"Error: Task '{task_key}' not found for video '{video_id}'.")
            else:
                print(f"Error: Video '{video_id}' not found in pending tasks.")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {pending_tasks_file}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) == 4:
        video_id = sys.argv[1]
        task_key = sys.argv[2]
        status = sys.argv[3]
        update_task_status(video_id, task_key, status)
    else:
        print("Usage: python update_task_status.py <video_id> <task_key> <status>")
        sys.exit(1)