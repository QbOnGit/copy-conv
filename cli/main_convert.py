# cli/main_convert.py

import sys, os
from core.config import IPHONE_IMAGE_EXTS, NON_IPHONE_IMAGE_EXTS, IPHONE_VIDEO_EXTS, NON_IPHONE_VIDEO_EXTS
from core.utils import (
    get_source_directory,
    get_destination_directory,
    yes_no_prompt
)
from datetime import datetime
from core.scanner import scan_and_deduplicate
from core.convert_images import process_images
from core.convert_videos import process_videos
from core.convert_slowmo import process_slowmo

def prompt_user_options():
    print("🎛️ Select media types to include in the process:")
    print("ℹ️ iPhone formats (converted):")
    print(f"   📸 Photos: {', '.join(sorted(IPHONE_IMAGE_EXTS))}")
    print(f"   🎞️ Videos: {', '.join(sorted(IPHONE_VIDEO_EXTS))}")
    print("ℹ️ Other formats (copied as-is if included):")
    print(f"   📸 Photos: {', '.join(sorted(NON_IPHONE_IMAGE_EXTS))}")
    print(f"   🎞️ Videos: {', '.join(sorted(NON_IPHONE_VIDEO_EXTS))}\n")
    types = ["photos", "videos", "slowmo"]
    user_options = {}

    for media_type in types:
        include = yes_no_prompt(f"Include {media_type}?")
        include_non_iphone = False
        if include:
            include_non_iphone = yes_no_prompt(f"→ Also include non-iPhone {media_type} formats?")
        user_options[media_type] = {
            "include": include,
            "include_non_iphone": include_non_iphone
        }

    return user_options

def main():
    print("📦 MEDIA CONVERSION & COPY UTILITY")

    source_dir = get_source_directory("Source path: ")
    output_dir = get_destination_directory("Destination path: ")

    # Create timestamped root subdir
    timestamp = datetime.now().strftime("copy-conv_%Y%m%d_%H%M%S")
    final_output_dir = os.path.join(output_dir, timestamp)
    os.makedirs(final_output_dir)

    user_options = prompt_user_options()

    print("\n📝 Summary:")
    print(f"Source directory:      {source_dir}")
    print(f"Destination directory: {final_output_dir}")
    for key in ["photos", "videos", "slowmo"]:
        opt = user_options[key]
        status = "✓" if opt["include"] else "✗"
        print(f"  - {key.capitalize():<7}: {status} (non-iPhone: {'yes' if opt['include_non_iphone'] else 'no'})")

    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != "y":
        print("❌ Aborted.")
        sys.exit(0)

    json_files = scan_and_deduplicate(source_dir, user_options, final_output_dir)

    if json_files.get("photos"):
        process_images(json_files["photos"], final_output_dir)
    if json_files.get("videos"):
        process_videos(json_files["videos"], final_output_dir)
    if json_files.get("slowmo"):
        process_slowmo(json_files["slowmo"], final_output_dir)

    print("\n✅ All steps completed successfully.")

if __name__ == "__main__":
    main()
