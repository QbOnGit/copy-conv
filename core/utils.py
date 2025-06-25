# core/utils.py

import os, shutil, subprocess, logging, json
from core.config import OUTPUT_VIDEO_EXT, LOG_FORMAT, REQUIRED_TOOLS, OUTPUT_IMAGE_EXT
from datetime import datetime, timedelta

def create_timestamped_log_path(output_dir, prefix):
    """
    Creates a log directory under output_dir/logs/<timestamp>/
    Returns full path to log file: .../logs/<timestamp>/<prefix>_<timestamp>.txt
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = os.path.join(output_dir, "logs", timestamp)
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{prefix}_{timestamp}.txt")
    return log_path

def get_source_directory(prompt):
    """
    Prompt user for a valid existing source directory.
    Provides instructions and verifies the path exists.
    """
    while True:
        print("📂 Please enter the full path to the SOURCE directory:")
        path = input(prompt).strip()
        if os.path.isdir(path):
            return os.path.abspath(path)
        elif os.path.exists(path):
            print("❌ That path exists but is not a directory.")
        else:
            print("❌ Directory does not exist.")

def get_destination_directory(prompt):
    """
    Prompt user for a destination directory path.
    Creates it if missing, unless a sibling with the same name already exists.
    """
    while True:
        print("📁 Please enter the full path for the DESTINATION directory (will be created if missing):")
        path = input(prompt).strip()
        if os.path.isdir(path):
            return os.path.abspath(path)
        elif os.path.exists(path):
            print("❌ That path exists but is not a directory.")
        else:
            parent = os.path.dirname(os.path.abspath(path))
            basename = os.path.basename(path)
            siblings = [d for d in os.listdir(parent) if os.path.isdir(os.path.join(parent, d))]
            if basename in siblings:
                print(f"❌ A directory named '{basename}' already exists in {parent}. Please choose another name.")
                continue
            try:
                os.makedirs(path)
                print(f"✅ Created directory: {path}")
                return os.path.abspath(path)
            except Exception as e:
                print(f"❌ Failed to create directory: {e}")

def yes_no_prompt(prompt, default="n"):
    """
    Prompt for a yes/no answer and return True/False.
    Accepts blank input as default value.
    """
    while True:
        ans = input(f"{prompt} (y/n): ").strip().lower()
        if not ans and default:
            ans = default
        if ans in ["y", "yes"]:
            return True
        elif ans in ["n", "no"]:
            return False
        else:
            print("❓ Please enter y or n.")

def check_required_tools(required_tools):
    missing = [tool for tool in required_tools if shutil.which(tool) is None]
    if missing:
        print(f"❌ Missing required tool(s): {', '.join(missing)}")
        exit(1)

def copy_file(src_path, dst_path):
    shutil.copy2(src_path, dst_path)

def convert_mov_to_mp4(src_path, dst_path_without_ext):
    dst_mp4 = dst_path_without_ext + OUTPUT_VIDEO_EXT
    subprocess.run([
        "ffmpeg", "-i", src_path, "-map_metadata", "0", "-c:v", "libx264",
        "-crf", "18", "-preset", "ultrafast", "-c:a", "aac", dst_mp4
    ], check=True)
    subprocess.run(["exiftool", "-TagsFromFile", src_path, "-overwrite_original", dst_mp4], check=True)

def convert_heic_to_jpg(src_path, dst_path_without_ext):
    dst_jpg = dst_path_without_ext + OUTPUT_IMAGE_EXT
    subprocess.run(["heif-convert", src_path, dst_jpg], check=True)
    subprocess.run(["exiftool", "-TagsFromFile", src_path, "-overwrite_original", dst_jpg], check=True)


def init_logging(log_path):
    logging.basicConfig(filename=log_path, level=logging.INFO, format=LOG_FORMAT)


def print_progress(idx, total, start_time, emoji="▶️"):
    elapsed = datetime.now() - start_time
    percent = (idx / total) * 100
    eta = timedelta(seconds=int((elapsed.total_seconds() / idx) * (total - idx)))
    print(f"{emoji} {idx}/{total} ({percent:.1f}%) — Elapsed: {elapsed} — ETA: ~{eta}", end="\r")

def load_checksum_map(json_path, required_tools_key):
    if not os.path.isfile(json_path):
        print(f"❌ Missing input file: {json_path}")
        return None
    check_required_tools(REQUIRED_TOOLS[required_tools_key])
    with open(json_path, "r") as f:
        return json.load(f)

def ensure_subfolder(output_dir, subfolder):
    full = os.path.join(output_dir, subfolder)
    os.makedirs(full, exist_ok=True)
    return full

def setup_logging(output_dir, prefix):
    log_path = create_timestamped_log_path(output_dir, prefix)
    init_logging(log_path)
    return log_path

def process_template(json_path, output_dir, subfolder, required_tools_key, process_func, filename_transform_func=None, emoji="▶️"):
    checksum_map = load_checksum_map(json_path, required_tools_key)
    if checksum_map is None:
        return

    subdir = ensure_subfolder(output_dir, subfolder)
    log_path = setup_logging(output_dir, f"log_{subfolder}")
    print(f"{emoji} Starting processing of {len(checksum_map)} files into /{subfolder}...")
    total = len(checksum_map)
    start_time = datetime.now()
    failures = 0

    for idx, (checksum, paths) in enumerate(checksum_map.items(), start=1):
        src = paths[0]
        original_name = os.path.basename(src)
        final_name = filename_transform_func(original_name) if filename_transform_func else original_name
        dst_path_wo_ext = os.path.splitext(os.path.join(subdir, final_name))[0]

        try:
            process_func(src, dst_path_wo_ext)
            logging.info(f"Processed: {src} → {dst_path_wo_ext}")
        except Exception as e:
            failures += 1
            logging.error(f"Error processing {src}: {e}")

        print_progress(idx, total, start_time, emoji)

    print(f"\n✅ Done. Log saved to {log_path}")
    if failures:
        print(f"⚠️ {failures} file(s) failed. See log for details.")
    logging.shutdown()

