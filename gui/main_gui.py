from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QFileDialog, QTextEdit, QLineEdit,
    QProgressBar, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QDateTime
import sys
import os

from core.scanner import scan_and_deduplicate
from core.convert_images import process_images
from core.convert_videos import process_videos
from core.convert_slowmo import process_slowmo


class WorkerThread(QThread):
    log = Signal(str)
    finished = Signal()
    progress = Signal(int)

    def __init__(self, source, destination, options):
        super().__init__()
        self.source = source
        self.destination = destination
        self.options = options

    def run(self):
        self.log.emit("🔍 Scanning and deduplicating files...")
        json_files = scan_and_deduplicate(self.source, self.options, self.destination)

        total_steps = sum(bool(json_files.get(k)) for k in ["photos", "videos", "slowmo"])
        completed = 0

        if json_files.get("photos"):
            self.log.emit("📸 Converting images...")
            process_images(json_files["photos"], self.destination)
            completed += 1
            self.progress.emit(int(completed / total_steps * 100))

        if json_files.get("videos"):
            self.log.emit("🎞️ Converting videos...")
            process_videos(json_files["videos"], self.destination)
            completed += 1
            self.progress.emit(int(completed / total_steps * 100))

        if json_files.get("slowmo"):
            self.log.emit("🐢 Converting slow-motion videos...")
            process_slowmo(json_files["slowmo"], self.destination)
            completed += 1
            self.progress.emit(int(completed / total_steps * 100))

        self.progress.emit(100)
        self.log.emit("✅ Done.")
        self.finished.emit()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📦 Media Convert & Copy")
        self.resize(600, 540)

        self.source_path = QLineEdit()
        self.dest_path = QLineEdit()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.photos_cb = QCheckBox("📸 Photos")
        self.photos_non_iphone_cb = QCheckBox("Include non-iPhone type files")
        self.videos_cb = QCheckBox("🎞️ Videos")
        self.videos_non_iphone_cb = QCheckBox("Include non-iPhone type files")
        self.slowmo_cb = QCheckBox("🐢 Slow motion videos")
        self.slowmo_non_iphone_cb = QCheckBox("Include non-iPhone type files")

        self.info_label = QLabel("\u26A0\ufe0f Non-iPhone files will be copied without conversion.")
        self.info_label.setWordWrap(True)
        self.info_label.setVisible(False)
        self.info_label.setStyleSheet("color: #aa6600; font-style: italic")

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Source directory:"))
        layout.addLayout(self._path_selector(self.source_path))

        layout.addWidget(QLabel("Destination directory:"))
        layout.addLayout(self._path_selector(self.dest_path))

        layout.addWidget(QLabel("\nCopy / Convert:"))
        layout.addLayout(self._media_option_row(self.photos_cb, self.photos_non_iphone_cb))
        layout.addLayout(self._media_option_row(self.videos_cb, self.videos_non_iphone_cb))
        layout.addLayout(self._media_option_row(self.slowmo_cb, self.slowmo_non_iphone_cb))

        layout.addWidget(self.info_label)

        start_button = QPushButton("🚀 Start Conversion")
        start_button.clicked.connect(self.start_process)
        layout.addWidget(start_button)

        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def _path_selector(self, line_edit):
        layout = QHBoxLayout()
        layout.addWidget(line_edit)
        button = QPushButton("Browse")
        button.clicked.connect(lambda: self._choose_dir(line_edit))
        layout.addWidget(button)
        return layout

    def _media_option_row(self, main_cb, sub_cb):
        layout = QHBoxLayout()
        layout.addWidget(main_cb)
        layout.addWidget(sub_cb)
        layout.addStretch()
        sub_cb.setEnabled(False)
        return layout

    def _connect_signals(self):
        self.photos_cb.stateChanged.connect(lambda: self._toggle_sub(self.photos_cb, self.photos_non_iphone_cb))
        self.videos_cb.stateChanged.connect(lambda: self._toggle_sub(self.videos_cb, self.videos_non_iphone_cb))
        self.slowmo_cb.stateChanged.connect(lambda: self._toggle_sub(self.slowmo_cb, self.slowmo_non_iphone_cb))

        self.photos_non_iphone_cb.stateChanged.connect(self._update_info_label)
        self.videos_non_iphone_cb.stateChanged.connect(self._update_info_label)
        self.slowmo_non_iphone_cb.stateChanged.connect(self._update_info_label)

    def _toggle_sub(self, main_cb, sub_cb):
        sub_cb.setEnabled(main_cb.isChecked())
        if not main_cb.isChecked():
            sub_cb.setChecked(False)
        self._update_info_label()

    def _update_info_label(self):
        show = any([
            self.photos_non_iphone_cb.isChecked(),
            self.videos_non_iphone_cb.isChecked(),
            self.slowmo_non_iphone_cb.isChecked()
        ])
        self.info_label.setVisible(show)

    def _choose_dir(self, line_edit):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            line_edit.setText(path)

    def _append_log(self, message):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.log_output.append(f"[{timestamp}] {message}")

    def start_process(self):
        source = self.source_path.text().strip()
        dest = self.dest_path.text().strip()

        if not os.path.isdir(source) or not dest:
            self._append_log("❌ Invalid source or destination path.")
            return

        options = {
            "photos": {
                "include": self.photos_cb.isChecked(),
                "include_non_iphone": self.photos_non_iphone_cb.isChecked()
            },
            "videos": {
                "include": self.videos_cb.isChecked(),
                "include_non_iphone": self.videos_non_iphone_cb.isChecked()
            },
            "slowmo": {
                "include": self.slowmo_cb.isChecked(),
                "include_non_iphone": self.slowmo_non_iphone_cb.isChecked()
            },
        }

        self.progress_bar.setValue(0)
        self.thread = WorkerThread(source, dest, options)
        self.thread.log.connect(self._append_log)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.finished.connect(lambda: self._append_log("🏁 All done."))
        self.thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
