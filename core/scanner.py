import os
import hashlib
import json
import subprocess
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.config import (
    IPHONE_IMAGE_EXTS,
    NON_IPHONE_IMAGE_EXTS,
    IPHONE_VIDEO_EXTS,
    NON_IPHONE_VIDEO_EXTS,
    SLOWMO_FPS_THRESHOLD
)

def is_slowmo_by_fps(file_path, threshold=SLOWMO_FPS_THRESHOLD):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            capture_output=True,
            text=True
        )
        raw = result.stdout.strip()
        if '/' in raw:
            num, denom = map(int, raw.split('/'))
            fps = num / denom
        else:
            fps = float(raw)

        return fps > threshold
    except Exception as e:
        print(f"⚠️ Could not read fps for {file_path}: {e}")
        return False

def compute_md5(file_path, chunk_size=8192):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_md5.update(chunk)
    return (file_path, hash_md5.hexdigest())

def classify_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext in IPHONE_IMAGE_EXTS or ext in NON_IPHONE_IMAGE_EXTS:
        return "photos"
    elif ext in IPHONE_VIDEO_EXTS or ext in NON_IPHONE_VIDEO_EXTS:
        return "slowmo" if is_slowmo_by_fps(file_path) else "videos"
    return None

def scan_and_deduplicate(source_dir, user_options, output_dir, max_workers=3):
    print("🔍 Scanning files...")
    file_list = []
    for root, _, files in os.walk(source_dir):
        for name in files:
            file_list.append(os.path.join(root, name))

    checksum_map = {
        "photos": {},
        "videos": {},
        "slowmo": {}
    }

    total = len(file_list)
    start_time = datetime.now()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(compute_md5, path): path for path in file_list}

        for idx, future in enumerate(as_completed(futures), start=1):
            file_path, checksum = future.result()
            category = classify_file(file_path)

            if category is None:
                continue

            if not user_options[category]["include"]:
                continue

            ext = os.path.splitext(file_path)[1].lower()
            is_iphone = (
                ext in IPHONE_IMAGE_EXTS or ext in IPHONE_VIDEO_EXTS
            )

            if not is_iphone and not user_options[category]["include_non_iphone"]:
                continue

            checksum_map[category].setdefault(checksum, []).append(file_path)

            elapsed = datetime.now() - start_time
            percent = (idx / total) * 100
            print(f"🧮 {idx}/{total} files ({percent:.1f}%) — Elapsed: {elapsed} — ETA: ~{timedelta(seconds=int((elapsed.total_seconds()/idx)*(total - idx)))}", end="\r")

    print("\n✅ Scan complete. Writing JSON files...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    data_root = os.path.join(output_dir, "data")
    json_subdir = os.path.join(data_root, timestamp)
    os.makedirs(json_subdir, exist_ok=True)
    json_paths = {}

    for cat in ["photos", "videos", "slowmo"]:
        if not user_options[cat]["include"]:
            continue
        output_path = os.path.join(json_subdir, f"{cat}_{timestamp}.json")
        with open(output_path, "w") as f:
            json.dump(checksum_map[cat], f, indent=2)
        json_paths[cat] = output_path
        print(f"📄 Saved {os.path.basename(output_path)} with {len(checksum_map[cat])} unique files.")

    return json_paths
