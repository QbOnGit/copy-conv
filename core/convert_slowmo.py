# core/convert_slowmo.py

import os
import json
import logging
from datetime import datetime, timedelta
from core.utils import create_timestamped_log_path, check_required_tools, copy_file, convert_mov_to_mp4, init_logging
from core.config import IPHONE_VIDEO_EXTS, OUTPUT_VIDEO_EXT, REQUIRED_TOOLS

def process_slowmo(json_path, output_dir):
    if not os.path.isfile(json_path):
        print(f"❌ Missing input file: {json_path}")
        return

    check_required_tools(REQUIRED_TOOLS["slowmo"])

    with open(json_path, "r") as f:
        checksum_map = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    log_path = create_timestamped_log_path(output_dir, "log_slowmo")
    init_logging(log_path)

    print(f"🐢 Starting conversion of {len(checksum_map)} unique slow-motion files...")
    total = len(checksum_map)
    start_time = datetime.now()
    failures = 0

    for idx, (checksum, paths) in enumerate(checksum_map.items(), start=1):
        src = paths[0]
        ext = os.path.splitext(src)[1].lower()
        original_name = os.path.basename(src)

        try:
            dst_file = os.path.join(output_dir, original_name)
            if ext in IPHONE_VIDEO_EXTS:
                dst_file = os.path.splitext(dst_file)[0] + OUTPUT_VIDEO_EXT
                convert_mov_to_mp4(src, os.path.splitext(dst_file)[0])
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