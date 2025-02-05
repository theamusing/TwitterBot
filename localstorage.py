import json
import os
import requests
from collections import deque

LOCAL_RECENT_IDS_FILE = "data/recent_ids.json"
LOCAL_POSTS_FOLDER = 'posts'

def load_recent_ids(max_len):
    try:
        with open(LOCAL_RECENT_IDS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return deque(data, maxlen=max_len)
    except (FileNotFoundError, json.JSONDecodeError):
        return deque(maxlen=max_len)

def save_recent_ids(recent_likes):
    try:
        with open(LOCAL_RECENT_IDS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(recent_likes), f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Save recent ids fail: {e}")

def save_posts(posts, storage_path):
    storage_dir = os.path.dirname(f"{storage_path}/{LOCAL_POSTS_FOLDER}")
    os.makedirs(storage_dir, exist_ok=True)

    for post in posts:
        post_id = post["tweet_id"]
        image_urls = post["images"]
        timestamp = post["timestamp"]
        safe_timestamp = timestamp.replace(":", "-")
        # save images
        for i, url in enumerate(image_urls):
            image_path = f"{storage_dir}/{post_id}_{safe_timestamp}_{i}.jpg"
            download_image(url, image_path)
    
def download_image(url, path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        response = requests.get(url)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(f"Download image fail: {e}")
