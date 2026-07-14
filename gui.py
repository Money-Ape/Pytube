import sys, os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit, QPushButton, QScrollArea, QGridLayout, QSizePolicy, QProgressBar)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont, QPixmap
from theme import THEMES

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def size_calc(self, size):
    units = ["Bytes", "KB", "MB", "GB", "TB"]
    for unit in units:
        if size < 1024 or unit == "TB":
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

class TubitUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme = THEMES["blue_gray"]

        self.setup_window()
        self.apply_theme()
        self.build_ui()

    def setup_window(self):
        self.setWindowTitle("Tubit")
        self.setWindowIcon(QIcon(resource_path("assets/Tubit.ico")))
        self.resize(620, 900)
        self.setMinimumSize(620, 900)
        
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
            QFrame#Card {{
                background : {self.w};
                border : 1px solid {self.b};
                border-radius : 14px;
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
        title = QLabel("Youtube Video Downloader")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))

        # ==================================================
        # SubTitle
        subtitle = QLabel("Fast • Simple • Reliable")
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
        url_title = QLabel("🔗 YouTube URL")
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

        # Assemble
        url_layout.addWidget(url_title)
        url_layout.addWidget(self.url_entry)
        url_layout.addWidget(self.fetch_btn)

        # ==================================================
        # Format card
        formats_card = QFrame()
        formats_card.setObjectName("Card")
        # formats_card.setMinimumHeight(340)
        formats_layout = QVBoxLayout(formats_card)
        formats_layout.setContentsMargins(20, 20, 20, 20)
        formats_layout.setSpacing(15)

        # ==================================================
        # ==================================================
        # Video information card
        video_card = QFrame()
        video_card.setObjectName("Card")

        video_layout = QVBoxLayout(video_card)
        video_layout.setContentsMargins(20, 20, 20, 20)
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
        self.thumbnail.setFixedSize(120, 69)
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
        self.video_duration = QLabel("Duration : --|--")
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
        self.download_btn.setMinimumHeight(42)
        self.download_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.download_btn.setEnabled(False)

        # ==================================================
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setVisible(True)
        self.progress.setMinimumHeight(18)

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
        # Scroll area
        self.format_scroll = QScrollArea()
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

        for i in range(8):
            card = self.format_card(
                "1080p",
                "MP4",
                "84 MB",
                "Video + Audio"
            )
            row = i // 2
            col = i % 2
            self.grid.addWidget(card, row, col)

        formats_layout.addWidget(formats_header)
        formats_layout.addWidget(self.format_scroll)

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
        else:
            self.fetch_btn.show()

    def format_card(self, quality, extension, size, media_type):
        card = QFrame()
        card.setObjectName("Card")
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setFixedHeight(90)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        # ==================================================
        # Quality
        quality_label = QLabel(f"{quality} * {extension}")
        quality_label.setFont(QFont("Segoe UI", 11, QFont.Bold))

        # ==================================================
        # Media type
        type_label = QLabel(media_type)
        type_label.setStyleSheet(f"""
            color : {self.st};
            font-size : 10pt;
        """)

        # ==================================================
        # Size
        size_label = QLabel(size)
        size_label.setStyleSheet(f"""
            color : {self.a};
            font-weight : 600;
            font-size : 10pt;
        """)

        # ==================================================
        # Assemble
        layout.addWidget(quality_label)
        layout.addWidget(type_label)
        layout.addStretch()
        layout.addWidget(size_label)

        return card


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TubitUI()
    window.show()

    sys.exit(app.exec())
