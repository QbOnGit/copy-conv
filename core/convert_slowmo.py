# core/convert_slowmo.py

from core.utils import copy_file, convert_mov_to_mp4, process_template
from core.config import IPHONE_VIDEO_EXTS, OUTPUT_VIDEO_EXT

def process_slowmo(json_path, output_dir):
    def convert_func(src, dst_wo_ext):
        ext = src.lower().split('.')[-1]
        if f".{ext}" in IPHONE_VIDEO_EXTS:
            convert_mov_to_mp4(src, dst_wo_ext)
        else:
            copy_file(src, dst_wo_ext + OUTPUT_VIDEO_EXT)

    process_template(
        json_path,
        output_dir,
        subfolder="slowmo",
        required_tools_key="slowmo",
        process_func=convert_func,
        filename_transform_func=lambda name: f"slowmo_{name}",
        emoji="🐢"
    )
