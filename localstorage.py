import json
import os
import requests
from collections import deque

LOCAL_STORAGE_FILE = "data/data.json"
LOCAL_POSTS_FOLDER = 'posts'

import json
import os
from collections import deque

def _load_json_key(file_path, key, default_value):
    try:
        if not os.path.exists(file_path):  # 文件不存在时，返回默认值
            return default_value

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get(key, default_value)  # 获取 key，若不存在则返回默认值
    except (FileNotFoundError, json.JSONDecodeError):
        return default_value

def _save_json_key(file_path, key, value):
    try:
        data = {}

        # 读取已有数据（如果文件存在）
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    pass  # 解析失败，保持 data 为空字典

        data[key] = value  # 更新 key 的值

        # 写回 JSON 文件
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Failed to save {key} to {file_path}: {e}")

def load_recent_ids(max_len):
    recent_ids = deque(_load_json_key(LOCAL_STORAGE_FILE, "recent", []), maxlen=max_len)
    return recent_ids

def save_recent_ids(recent_ids):
    _save_json_key(LOCAL_STORAGE_FILE, "recent", list(recent_ids))

def load_autoliked_ids(max_len, username):
    autoliked_ids = deque(_load_json_key(LOCAL_STORAGE_FILE, "autolike", {}).get(username, []), maxlen=max_len)
    return autoliked_ids

def save_autoliked_ids(autoliked_ids, username):
    data = _load_json_key(LOCAL_STORAGE_FILE, "autolike", {})
    data[username] = list(autoliked_ids)
    _save_json_key(LOCAL_STORAGE_FILE, "autolike", data)

def save_posts(posts, storage_path):
    storage_dir = os.path.join(storage_path, LOCAL_POSTS_FOLDER)
    os.makedirs(storage_dir, exist_ok=True)
    print(f"Saving posts to {storage_dir}")

    for post in posts:
        post_id = post["tweet_id"]
        image_urls = post["images"]
        timestamp = post["timestamp"]
        safe_timestamp = timestamp.replace(":", "-")
        # save images
        for i, url in enumerate(image_urls):
            image_path = f"{storage_dir}/{post_id}_{safe_timestamp}_{i}.jpg"
            print(f"Downloading image {i+1}/{len(image_urls)} for post {post_id}")
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
