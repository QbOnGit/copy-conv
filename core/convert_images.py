# core/convert_images.py

import os
import json
import logging
import subprocess
from datetime import datetime, timedelta
from core.utils import create_timestamped_log_path, check_required_tools, copy_file, init_logging
from core.config import IPHONE_IMAGE_EXTS, OUTPUT_IMAGE_EXT, REQUIRED_TOOLS

def convert_heic_to_jpg(src_path, dst_path_without_ext):
    dst_jpg = dst_path_without_ext + OUTPUT_IMAGE_EXT
    subprocess.run(["heif-convert", src_path, dst_jpg], check=True)
    subprocess.run(["exiftool", "-TagsFromFile", src_path, "-overwrite_original", dst_jpg], check=True)

def process_images(json_path, output_dir):
    if not os.path.isfile(json_path):
        print(f"❌ Missing input file: {json_path}")
        return

    check_required_tools(REQUIRED_TOOLS["images"])

    with open(json_path, "r") as f:
        checksum_map = json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    log_path = create_timestamped_log_path(output_dir, "log_images")
    init_logging(log_path)

    print(f"📸 Starting conversion of {len(checksum_map)} unique image files...")
    total = len(checksum_map)
    start_time = datetime.now()
    failures = 0

    for idx, (checksum, paths) in enumerate(checksum_map.items(), start=1):
        src = paths[0]
        ext = os.path.splitext(src)[1].lower()
        original_name = os.path.basename(src)

        try:
            dst_file = os.path.join(output_dir, original_name)
            if ext in IPHONE_IMAGE_EXTS:
                dst_file = os.path.splitext(dst_file)[0] + OUTPUT_IMAGE_EXT
                convert_heic_to_jpg(src, os.path.splitext(dst_file)[0])
            else:
                copy_file(src, dst_file)

            logging.info(f"Processed: {src} → {dst_file}")
        except Exception as e:
            failures += 1
            logging.error(f"Error processing {src}: {e}")

        elapsed = datetime.now() - start_time
        percent = (idx / total) * 100
        eta = timedelta(seconds=int((elapsed.total_seconds() / idx) * (total - idx)))
        print(f"▶️ {idx}/{total} ({percent:.1f}%) — Elapsed: {elapsed} — ETA: ~{eta}", end="\r")

    print("\n✅ Done. Log saved to:", log_path)


    if failures:
        print(f"⚠️ Completed with {failures} failure(s). See log for details.")

    logging.shutdown()