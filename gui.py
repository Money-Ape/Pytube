import sys, os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit, QPushButton, QScrollArea, QGridLayout, QSizePolicy, QProgressBar, QButtonGroup, QRadioButton)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from theme import THEMES
from tubit import TubitBack

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class TubitUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme = THEMES["blue_gray"]

        self.format_mode = "video"
        self.all_formats = []

        self.setup_window()
        self.apply_theme()
        self.build_ui()

        self.backend = TubitBack()
        self.selected_format = None
        self.selected_card = None
        self.net = QNetworkAccessManager(self)
        self.net.finished.connect(self.thumbnail_loaded)

        self.backend.formats_loaded.connect(self.populate_formats)
        self.backend.error.connect(self.backend_error)
        self.backend.download_progress.connect(self.update_progress)
        self.backend.download_finished.connect(self.download_complete)
        self.backend.download_error.connect(self.backend_error)

    def setup_window(self):
        self.setWindowTitle("Tubit")
        self.setWindowIcon(QIcon(resource_path("assets/Tubit.ico")))
        self.resize(700, 900)
        self.setMinimumSize(700, 900)
        
        self.scroll_win = QScrollArea()
        self.scroll_win.setWidgetResizable(True)
        self.scroll_win.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_win.setFrameShape(QFrame.Shape.NoFrame)
        
        self.page = QWidget()
        self.scroll_win.setWidget(self.page)
        self.setCentralWidget(self.scroll_win)

    def apply_theme(self):
        self.win = self.theme["window"]
        self.w = self.theme["workspace"]
        self.i = self.theme["interactive"]
        self.a = self.theme["accent"]
        self.ah = self.theme["accent_hover"]
        self.b = self.theme["border"]
        self.t = self.theme["text"]
        self.st = self.theme["subtext"]
        self.suck = self.theme["success"]
        self.warn = self.theme["warning"]
        self.selc = self.theme["selected"]

        self.setStyleSheet(f"""
            QMainWindow {{
                background : {self.win};
            }}
            QWidget {{
                background : {self.w};
                color : {self.t};
                font-family : "Segoe UI";
                font-size : 11pt;
            }}
            QLabel {{
                background : transparent;
                color : {self.t};
            }}
            QFrame#FormatCard {{
                background : {self.w};
                border : 1px solid {self.b};
                border-radius : 12px;
            }}
            QFrame#FormatCard[selected="true"] {{
                background : #384455;
                border : 2px solid {self.a};
            }}
            QFrame#FormatCard:hover {{
                border:2px solid #6E87A5;
                background:#303A46;
            }}
            QLineEdit {{
                background : {self.i};
                border : 1px solid {self.b};
                border-radius : 10px;
                padding : 10px 14px;
                color : {self.t};
            }}
            QLineEdit:hover {{
                border : 1px solid {self.a};
            }}
            QLineEdit:focus {{
                border : 2px solid {self.a};
            }}
            QPushButton {{
                background : {self.a};
                border : none;
                border-radius : 10px;
                color : white;
                font-size : 11pt;
                font-weight : 600;
                padding : 10px 18px;
            }}
            QPushButton:hover {{
                background : {self.ah};
            }}
            QPushButton:pressed {{
                background : {self.selc};
                padding-top : 11px;
                padding-left : 19px;
            }}
            QPushButton:disabled {{
                background : {self.i};
                color : {self.st};
            }}
            QScrollArea {{
                background : transparent;
                border : none;
            }}
            ScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background : {self.b};
                border-radius :5px;
                min-height : 40px;
            }}
            QScrollBar::handle:vertical:hover {{
                background : {self.a};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height : 0px;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background : transparent;
            }}
            QScrollArea > QWidget > QWidget {{
                background : transparent;
            }}
            QProgressBar {{
                background : {self.i};
                border : none;
                border-radius : 8px;
                text-align : center;
                color : {self.t};
                font-weight : 600;
            }}
            QProgressBar::chunk {{
                background : {self.a};
                border-radius : 8px;
            }}
        """)

    def build_ui(self):
        # ==================================================
        # Header Container
        header = QWidget()
        header.setStyleSheet("background : transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(15)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ==================================================
        # Logo
        logo = QLabel()
        pixmap = QPixmap(resource_path("assets/Tubit.png"))
        logo.setPixmap(
            pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )

        # ==================================================
        # Title Area 
        title_cnt = QWidget()
        title_cnt.setStyleSheet("background : transparent;")
        title_layout = QVBoxLayout(title_cnt)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        # ==================================================
        # TItle
        title = QLabel("Video Downloader")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))

        # ==================================================
        # SubTitle
        subtitle = QLabel("Youtube | Instagram\nFast • Simple • Reliable")
        subtitle.setStyleSheet(f"""
            color : {self.st};
            font-size : 11pt;
            background : transparent;
        """)

        # ==================================================
        # Layout
        main_layout = QVBoxLayout(self.page)
        main_layout.setContentsMargins(25, 20, 25, 25)
        main_layout.setSpacing(24)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ==================================================
        # Header
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addWidget(logo)
        header_layout.addWidget(title_cnt)
        main_layout.addWidget(header)

        # ==================================================
        # ==================================================
        # URL card
        url_card = QFrame()
        url_card.setObjectName("Card")
        url_layout = QVBoxLayout(url_card)
        url_layout.setContentsMargins(20, 20, 20, 20)
        url_layout.setSpacing(15)

        # ==================================================
        # URL title
        url_title = QLabel("🔗 URL (Youtube | Instagram)")
        url_title.setFont(QFont("Segoe UI", 12, QFont.Bold))

        # ==================================================
        # URL entry
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Paste a YouTube URL here...")
        self.url_entry.setMinimumHeight(42)

        # ==================================================
        # Fetch button
        self.fetch_btn = QPushButton("Fetch Available Formats")
        self.fetch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fetch_btn.setMinimumHeight(42)
        self.fetch_btn.hide()

        self.url_entry.textChanged.connect(self.toggle_fetch_btn)
        self.fetch_btn.clicked.connect(self.fetch_formats)

        # Assemble
        url_layout.addWidget(url_title)
        url_layout.addWidget(self.url_entry)
        url_layout.addWidget(self.fetch_btn)

        # ==================================================
        # Format card
        formats_card = QFrame()

        formats_line_1 = QFrame()
        formats_line_1.setFrameShape(QFrame.Shape.HLine)
        formats_line_1.setStyleSheet(f"""
            color:{self.b};
        """)

        formats_line_2 = QFrame()
        formats_line_2.setFrameShape(QFrame.Shape.HLine)
        formats_line_2.setStyleSheet(f"""
            color:{self.b};
        """)

        formats_card.setObjectName("Card")
        formats_layout = QVBoxLayout(formats_card)
        formats_layout.setContentsMargins(20, 20, 20, 20)
        formats_layout.setSpacing(15)

        # ==================================================
        # ==================================================
        # Video information card
        video_card = QFrame()
        video_card.setObjectName("Card")

        video_layout = QVBoxLayout(video_card)
        video_layout.setContentsMargins(16, 16, 16, 16)
        video_layout.setSpacing(15)

        # ==================================================
        # Video header
        video_header = QLabel("Video insights")
        video_header.setFont(QFont("Segoe UI", 12, QFont.Bold))

        # ==================================================
        # Information container
        video_info = QWidget()
        video_info_layout = QHBoxLayout(video_info)
        video_info_layout.setContentsMargins(0, 0, 0, 0)
        video_info_layout.setSpacing(15)

        # ==================================================
        # Thumnail placeholder
        self.thumbnail = QLabel()
        self.thumbnail.setFixedSize(96, 54)
        self.thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.thumbnail.setStyleSheet(f"""
            background:{self.i};
            border:1px solid {self.b};
            border-radius:8px;
            color:{self.st};
        """)
        self.thumbnail.setText("Thumbnail")

        # ==================================================
        # Video details
        details = QWidget()
        details_layout = QVBoxLayout(details)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(6)

        # Video title
        self.video_title = QLabel("No video loaded.!")
        self.video_title.setWordWrap(True)
        self.video_title.setFont(QFont("Segoe UI", 11, QFont.Bold))

        # Channel
        self.video_channel = QLabel("Channel : ---")
        self.video_channel.setStyleSheet(f"""
            color : {self.st};
        """)

        # Duration
        self.video_duration = QLabel("Duration : --:--")
        self.video_duration.setStyleSheet(f"""
            color : {self.st};
        """)

        # Assemble details
        details_layout.addWidget(self.video_title)
        details_layout.addWidget(self.video_channel)
        details_layout.addWidget(self.video_duration)
        details_layout.addStretch()

        # Assemble information
        video_info_layout.addWidget(self.thumbnail)
        video_info_layout.addWidget(details)

        # Assemble card
        video_layout.addWidget(video_header)
        video_layout.addWidget(video_info)

        # ==================================================
        # ==================================================
        # Download card
        download_card = QFrame()
        download_card.setObjectName("Card")
        download_layout = QVBoxLayout(download_card)
        download_layout.setContentsMargins(20, 20, 20, 20)
        download_layout.setSpacing(15)

        # ==================================================
        # Header
        download_title = QLabel("Download")
        download_title.setFont(QFont("Segoe UI", 12, QFont.Bold))

        # ==================================================
        # Selected format
        selected_title = QLabel("Selected Format")
        selected_title.setStyleSheet(f"""
            color : {self.st};
            font-size : 10pt;
        """)

        self.selected_format_label = QLabel("No Format Selected")
        self.selected_format_label.setFont(QFont("Segoe UI", 11, QFont.Bold))

        # ==================================================
        # Download button
        self.download_btn = QPushButton("Download")
        self.download_btn.setMinimumHeight(36)
        self.download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_btn.clicked.connect(self.download_video)

        self.download_btn.setEnabled(False)

        # ==================================================
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setVisible(True)
        self.progress.setMinimumHeight(14)

        # ==================================================
        # Status
        self.download_status_label = QLabel("Waiting...")
        self.download_status_label.setStyleSheet(f"""
            color : {self.st};
        """)

        # ==================================================
        # Assemble
        download_layout.addWidget(download_title)
        download_layout.addWidget(selected_title)
        download_layout.addWidget(self.selected_format_label)
        download_layout.addSpacing(5)

        download_layout.addWidget(self.download_btn)
        download_layout.addSpacing(8)

        download_layout.addWidget(self.progress)
        download_layout.addWidget(self.download_status_label)

        # ==================================================
        # ==================================================
        # Format header
        formats_header = QWidget()
        formats_header.setStyleSheet("background : transparent;")
        formats_header_layout = QHBoxLayout(formats_header)
        formats_header_layout.setContentsMargins(0, 0, 0, 0)
        formats_header_layout.setSpacing(10)

        # ==================================================
        # Format title
        formats_title = QLabel("Available Formats")
        formats_title.setFont(QFont("Segoe UI",12,QFont.Bold))
        self.format_count = QLabel("0")
        self.format_count.setStyleSheet(f"""
            color : {self.st}
        """)

        formats_header_layout.addWidget(formats_title)
        formats_header_layout.addStretch()
        formats_header_layout.addWidget(self.format_count)

        # ==================================================
        # filter Formats
        self.filter_group = QButtonGroup(self)

        self.video_btn = QRadioButton("Video")
        self.video_only_btn = QRadioButton("Video Only")
        self.audio_only_btn = QRadioButton("Audio Only")

        self.video_btn.setChecked(True)

        self.filter_group.addButton(self.video_btn)
        self.filter_group.addButton(self.video_only_btn)
        self.filter_group.addButton(self.audio_only_btn)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(20)

        filter_row.addWidget(self.video_btn)
        filter_row.addWidget(self.video_only_btn)
        filter_row.addWidget(self.audio_only_btn)
        filter_row.addStretch()

        self.video_btn.toggled.connect(self.filter_formats)
        self.video_only_btn.toggled.connect(self.filter_formats)
        self.audio_only_btn.toggled.connect(self.filter_formats)

        # ==================================================
        # Scroll area
        self.format_scroll = QScrollArea()
        self.format_scroll.setMinimumHeight(400)
        self.format_scroll.setWidgetResizable(True)
        self.format_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.format_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # ==================================================
        # Format container
        self.format_ctn = QWidget()
        self.grid = QGridLayout(self.format_ctn)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(12)

        self.format_scroll.setWidget(self.format_ctn)

        self.empty_formats = QLabel(
            "Paste a YouTube URL and click\n"
            "\"Fetch Available Formats\""
        )
        self.empty_formats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_formats.setStyleSheet(f"""
            color: {self.st};
            font-size: 11pt;
        """)

        self.grid.addWidget(
            self.empty_formats,
            0, 0, 1, 2
        )
        formats_layout.addWidget(formats_header)
        formats_layout.addLayout(filter_row)
        formats_layout.addWidget(formats_line_1)
        formats_layout.addWidget(self.format_scroll)
        formats_layout.addWidget(formats_line_2)

        # ==================================================
        # Assemble
        url_layout.addWidget(url_title)
        url_layout.addWidget(self.url_entry)
        url_layout.addWidget(self.fetch_btn)

        main_layout.addWidget(url_card)
        main_layout.addWidget(formats_card)
        main_layout.addWidget(video_card)
        main_layout.addWidget(download_card)

    def toggle_fetch_btn(self):
        if not self.url_entry.text().strip():
            self.fetch_btn.hide()
            self.fetch_btn.hide()
            self.format_count.setText("0")
            self.video_title.setText("No video loaded.!")
            self.video_channel.setText("Channel : ---")
            self.video_duration.setText("Duration : --:--")
            self.thumbnail.clear()
            self.thumbnail.setText("Thumbnail")

        else:
            self.fetch_btn.show()

    def format_card(self, fmt):
        card = QFrame()
        card.mousePressEvent = (
            lambda e, f=fmt, c=card:
            self.select_format(f, c)
        )
        card.setObjectName("FormatCard")
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setFixedSize(250, 110)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        # ==================================================
        # Quality
        quality_label = QLabel(f"{fmt['quality']} • {fmt['extension']}")
        quality_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        quality_label.setFixedHeight(24)

        # ==================================================
        # Media type
        codec_label = QLabel(fmt["codec"].upper())
        codec_label.setStyleSheet(f"""
            color:{self.st};
            font-size:9pt;
        """)

        # ==================================================
        # Size
        size_label = QLabel(fmt["size"])
        size_label.setStyleSheet(f"""
            color : {self.a};
            font-weight : 600;
            font-size : 10pt;
        """)
        size_label.setFixedHeight(20)

        # ==================================================
        # Assemble
        layout.addWidget(quality_label)
        layout.addWidget(codec_label)
        layout.addStretch()
        layout.addWidget(size_label)

        return card

    def select_format(self, fmt, card):
        if self.selected_card:
            self.selected_card.setProperty("selected", False)
            self.selected_card.style().unpolish(self.selected_card)
            self.selected_card.style().polish(self.selected_card)
        
        self.selected_card = card
        card.setProperty("selected", True)
        card.style().unpolish(card)
        card.style().polish(card)

        self.selected_format = fmt

        self.selected_format_label.setText(
            f"✓ {fmt['quality']} • "
            f"{fmt['extension']} • "
            f"{fmt['size']}"
        )
        self.download_btn.setEnabled(True)

    def fetch_formats(self):
        if self.backend.fetch_worker and self.backend.fetch_worker.isRunning():
            return

        url = self.url_entry.text().strip()
        if not url:
            return

        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("Fetching...")
        self.backend.fetch_formats(url)

    def load_thumbnail(self, url):
        if not url:
            self.thumbnail.clear()
            self.thumbnail.setText("Thumbnail")
            return
        
        request = QNetworkRequest(QUrl(url))
        self.net.get(request)

    def thumbnail_loaded(self, reply):
        if reply.error() != QNetworkReply.NetworkError.NoError:
            self.thumbnail.clear()
            self.thumbnail.setText("Thumbnail")
            reply.deleteLater()
            return
        
        data = reply.readAll()
        pix = QPixmap()
        pix.loadFromData(data)
        if not pix.isNull():
            self.thumbnail.setPixmap(
                pix.scaled(
                    self.thumbnail.width(),
                    self.thumbnail.height(),       
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
            self.thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)

        else:
            self.thumbnail.clear()
            self.thumbnail.setText("Thumbnail")
        
        reply.deleteLater()

    def download_video(self):
        if self.selected_format is None:
            return

        self.download_btn.setEnabled(False)
        self.fetch_btn.setEnabled(False)
        self.progress.setValue(0)
        self.download_status_label.setText("Starting download...")

        if self.format_mode == "video":
            format_string = (f"{self.selected_format['format_id']}+bestaudio/best")

        elif self.format_mode == "video_only":
            format_string = self.selected_format["format_id"]

        else:
            format_string = self.selected_format["format_id"]

        self.backend.download(self.url_entry.text().strip(), format_string)

    def update_progress(self, value, status):
        self.progress.setValue(int(value))
        self.download_status_label.setText(status)

    def download_complete(self):
        self.progress.setValue(100)
        self.download_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)
        self.download_status_label.setText("Download complete successfully.!")
        QTimer.singleShot(1500, lambda: self.progress.setValue(0))

    def backend_error(self, mesg):
        self.fetch_btn.setEnabled(True)
        self.thumbnail.clear()
        self.thumbnail.setText("Thumbnail")
        self.download_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch Available Formats")

        self.download_status_label.setText(mesg)

    def filter_formats(self):
        self.selected_format = None
        self.selected_card = None
        self.download_btn.setEnabled(False)
        self.selected_format_label.setText("No Formats Selected.!")
        if self.video_btn.isChecked():
            self.format_mode = "video"

        elif self.video_only_btn.isChecked():
            self.format_mode = "video_only"

        else:
            self.format_mode = "audio_only"

        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        visible = []
        if self.format_mode == "video":
            visible = [
                fmt for fmt in self.all_formats
                if fmt["has_video"]
            ]

        elif self.format_mode == "video_only":
            visible = [
                fmt for fmt in self.all_formats
                if fmt["has_video"]
            ]

        else:
            visible = [
                fmt for fmt in self.all_formats
                if fmt["has_audio"] and not fmt["has_video"]
            ]

        self.format_count.setText(str(len(visible)))
        if not visible:
            self.grid.addWidget(
                QLabel("No Formats Available.!"), 0, 0
            )
            return
        
        for i, fmt in enumerate(visible):
            card = self.format_card(fmt)
            row = i // 2
            col = i % 2 
            self.grid.addWidget(card, row, col)

    def populate_formats(self, info, formats):
        self.all_formats = formats
        self.video_info = info

        self.selected_format = None
        self.selected_card = None
        self.progress.setValue(0)
        self.selected_format_label.setText("No Format Selected.!")

        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch Available Formats")

        self.video_title.setText(info.get("title", "Unknown"))
        self.video_channel.setText(f"Channel : {info.get('uploader','Unknown')}")
        self.video_duration.setText(f"Duration : {info.get('duration_string','--:--')}")
        self.load_thumbnail(info.get("thumbnail"))

        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.filter_formats()

        self.download_btn.setEnabled(False)
        self.selected_format_label.setText("No Format Selected.!")
        self.download_status_label.setText("Select a format to continue.")

    def closeEvent(self, event):
        self.backend.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TubitUI()
    window.show()

    sys.exit(app.exec())
