# core/convert_videos.py

from core.utils import copy_file, convert_mov_to_mp4, process_template
from core.config import IPHONE_VIDEO_EXTS, OUTPUT_VIDEO_EXT

def process_videos(json_path, output_dir):
    def convert_func(src, dst_wo_ext):
        ext = src.lower().split('.')[-1]
        if f".{ext}" in IPHONE_VIDEO_EXTS:
            convert_mov_to_mp4(src, dst_wo_ext)
        else:
            copy_file(src, dst_wo_ext + OUTPUT_VIDEO_EXT)

    process_template(
        json_path,
        output_dir,
        subfolder="movies",
        required_tools_key="videos",
        process_func=convert_func,
        emoji="🎞️"
    )
