# core/config.py

# iPhone-native image formats (converted using heif-convert + exiftool)
IPHONE_IMAGE_EXTS = {".heic", ".heif"}

# iPhone-native video formats (converted using ffmpeg + exiftool)
IPHONE_VIDEO_EXTS = {".mov"}

# Common non-iPhone image formats (copied as-is if user opts in)
NON_IPHONE_IMAGE_EXTS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif", ".webp"
}

# Common non-iPhone video formats (copied as-is if user opts in)
NON_IPHONE_VIDEO_EXTS = {
    ".mp4", ".avi", ".mkv", ".webm", ".mts", ".m2ts", ".wmv", ".flv"
}

# Unified sets
ALL_IMAGE_EXTS = IPHONE_IMAGE_EXTS | NON_IPHONE_IMAGE_EXTS
ALL_VIDEO_EXTS = IPHONE_VIDEO_EXTS | NON_IPHONE_VIDEO_EXTS

# Output formats
OUTPUT_IMAGE_EXT = ".jpg"
OUTPUT_VIDEO_EXT = ".mp4"

# Minimum FPS to classify as slow-motion (used with ffprobe)
SLOWMO_FPS_THRESHOLD = 100

# External tools required
REQUIRED_TOOLS = {
    "images": ["heif-convert", "exiftool"],
    "videos": ["ffmpeg", "exiftool"],
    "slowmo": ["ffmpeg", "exiftool"]
}

# Logging format (for consistency across modules)
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
