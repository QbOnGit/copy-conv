# core/convert_images.py

from core.utils import copy_file, convert_heic_to_jpg, process_template
from core.config import IPHONE_IMAGE_EXTS

def process_images(json_path, output_dir):
    def convert_func(src, dst_wo_ext):
        ext = src.lower().split('.')[-1]
        if f".{ext}" in IPHONE_IMAGE_EXTS:
            convert_heic_to_jpg(src, dst_wo_ext)
        else:
            copy_file(src, dst_wo_ext + ".jpg")

    process_template(
        json_path,
        output_dir,
        subfolder="images",
        required_tools_key="images",
        process_func=convert_func,
        emoji="📸"
    )
