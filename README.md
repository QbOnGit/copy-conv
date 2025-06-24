# Media Convert Tool

A command-line utility for scanning, deduplicating, and converting media files — especially useful for iPhone photo/video libraries. It detects duplicates, converts `.HEIC` to `.JPG` and `.MOV` to `.MP4`, and can process slow-motion videos based on frame rate.

## 📦 Features

- 📂 Recursive scan of source directory for media files
- 🧠 Deduplication using MD5 checksums
- 🖼️ Converts iPhone `.heic` to `.jpg` with metadata preserved (ExifTool)
- 🎞️ Converts iPhone `.mov` to `.mp4` with metadata (ffmpeg + ExifTool)
- 🐢 Detects and processes slow-motion videos
- 📝 Logs all operations into timestamped files
- ✅ Optional inclusion of non-iPhone formats

## 🛠️ Requirements

Install required system tools:

```bash
sudo apt install ffmpeg exiftool libheif-examples
```

Python packages:

```bash
pip install -r requirements.txt
```

> Python standard library is used — no external packages required.

## 🚀 Usage

Run from the command line:

```bash
python3 cli/main_convert.py
```

You'll be prompted to:
- Choose media types: photos, videos, slow-motion
- Decide whether to include non-iPhone formats
- Set source and destination directories
- Confirm before starting

Output files are organized into:
- `/logs/<timestamp>/` – logs for each conversion step
- `/data/<timestamp>/` – JSON files listing deduplicated files

## 📁 Project Structure

```text
media_convert_tool/
├── core/                  # Logic modules
│   ├── scanner.py         # Scans & deduplicates files
│   ├── convert_images.py  # Converts images
│   ├── convert_videos.py  # Converts videos
│   ├── convert_slowmo.py  # Converts slow-motion
│   ├── config.py          # File types & tool config
│   └── utils.py           # Common utilities
├── cli/
│   └── main_convert.py    # CLI entry point
├── .gitignore
├── .pipreqs-ignore
├── requirements.txt
└── README.md
```

## 🪪 License

MIT License
