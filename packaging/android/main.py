import os, re, sys, threading, yt_dlp, traceback, shutil, subprocess
from pathlib import Path
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage, Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex, platform
from theme import THEMES

print("=" * 50)
print("Platform :", platform)
print("Python   :", sys.version)
print("yt-dlp   :", yt_dlp.version.__version__)
print("=" * 50)

THEME = THEMES["blue_gray"]
SELECTED_CARD_BG = "#384455"

ALLOW_STREAM_MERGE = True

def resource_path(relative_path):
    """Same helper as tubit.py/gui.py, for locating bundled assets (e.g. the
    app icon) whether running from source or a packaged build."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# ==================================================
# Android storage / permissions helpers
# ==================================================
def get_download_dir():
    if platform == "android":
        try:
            if platform == "android":
                from android.permissions import Permission, request_permissions
                from android.storage import primary_external_storage_path

                request_permissions([
                    Permission.INTERNET,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE,
                ])

                download_dir = os.path.join(primary_external_storage_path(), "Download", "Tubit")

            else:
                download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Tubit")

        except Exception as e:
            print(f"[Storage] falling back, could not resolve android storage: {e}")
            download_dir = os.path.join(os.path.expanduser("~"), "Tubit")
    else:
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Tubit")

    os.makedirs(download_dir, exist_ok=True)
    return download_dir


# ==================================================
# ffmpeg binary location
# ==================================================
def get_ffmpeg_path():
    if platform == "android":
        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            native_lib_dir = PythonActivity.mActivity.getApplicationInfo().nativeLibraryDir
            ffmpeg_path = os.path.join(native_lib_dir, "libffmpegbin.so")

            if os.path.exists(ffmpeg_path):
                return ffmpeg_path

            print(f"[ffmpeg] Expected binary not found at {ffmpeg_path}")
            return "ffmpeg"

        except Exception as e:
            error_mesg = str(e)
            print(f"[ffmpeg] Could not resolve native lib dir: {error_mesg}")
            return "ffmpeg"

    return "ffmpeg"

def format_file_size(size):
    if size is None:
        return "Unknown"

    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} PB"


# ==================================================
# Background workers (plain threads, not QThread)
# ==================================================
class FetchWorker(threading.Thread):
    def __init__(self, url, on_done, on_error):
        super().__init__(daemon=True)
        self.url = url
        self.on_done = on_done
        self.on_error = on_error

    def run(self):
        try:
            print("=" * 60)
            print("FetchWorker started")
            print("Platform :", platform)
            print("Python   :", sys.version)
            print("yt-dlp   :", yt_dlp.version.__version__)
            print("URL      :", self.url)
            print("=" * 60)

            print("sys.stdout :", type(sys.stdout), sys.stdout)
            print("sys.stderr :", type(sys.stderr), sys.stderr)
            print("stdout.write :", hasattr(sys.stdout, "write"))
            print("stderr.write :", hasattr(sys.stderr, "write"))

            print("STEP 1 : Building YoutubeDL options")

            class Logger:
                def debug(self, msg):
                    print("[DEBUG]", msg)

                def warning(self, msg):
                    print("[WARNING]", msg)

                def error(self, msg):
                    print("[ERROR]", msg)

            opts = {
                "quiet": False,
                "skip_download": True,
                "logger": Logger(),
                "progress_hooks": [
                    lambda d: print("HOOK:", d.get("status"))
                ],
            }

            print("STEP 2 : Creating YoutubeDL")

            ydl = yt_dlp.YoutubeDL(opts)

            print("STEP 3 : Calling extract_info()")

            info = ydl.extract_info(self.url, download=False)

            print("STEP 4 : extract_info() returned")

            formats = info.get("formats", [])
            print(f"Formats found : {len(formats)}")

            processed = []

            for fmt in formats:

                processed.append({
                    "format_id": fmt.get("format_id"),
                    "quality": fmt.get("format_note")
                               or fmt.get("resolution")
                               or "Unknown",
                    "extension": fmt.get("ext"),
                    "codec": fmt.get("vcodec")
                              if fmt.get("vcodec") != "none"
                              else fmt.get("acodec"),
                    "size": format_file_size(
                        fmt.get("filesize")
                        or fmt.get("filesize_approx")
                    ),
                    "has_video": fmt.get("vcodec") != "none",
                    "has_audio": fmt.get("acodec") != "none",
                })

            print("STEP 5 : Scheduling UI update")

            Clock.schedule_once(
                lambda dt: self.on_done(info, processed)
            )

            print("FetchWorker completed successfully")

        except BaseException as e:

            print("=" * 60)
            print("FetchWorker FAILED")
            print("Exception Type :", type(e).__name__)
            print("Exception      :", repr(e))
            print("=" * 60)

            traceback.print_exc()
            error_message = str(e)
            def notify(dt):
                self.on_error(error_message)

            Clock.schedule_once(notify)

class Logger:
    def debug(self, msg):
        print("[DEBUG]", msg)

    def warning(self, msg):
        print("[WARNING]", msg)

    def error(self, msg):
        print("[ERROR]", msg)

class DownloadWorker(threading.Thread):
    def __init__(self, url, format_id, download_dir, on_progress, on_done, on_error):
        super().__init__(daemon=True)
        self.url = url
        self.format_id = format_id
        self.download_dir = download_dir
        self.on_progress = on_progress
        self.on_done = on_done
        self.on_error = on_error

    def progress_hook(self, d):
        if d["status"] != "downloading":
            return

        ansi = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        percent_text = ansi.sub("", d.get("_percent_str", "0%"))
        match = re.search(r"(\d+(?:\.\d+)?)", percent_text)
        value = float(match.group(1)) if match else 0.0

        speed = ansi.sub("", d.get("_speed_str", ""))
        eta = ansi.sub("", d.get("_eta_str", ""))

        status = f"{value:.1f}%"
        if speed:
            status += f" - {speed}"
        if eta:
            status += f" - ETA {eta}"

        Clock.schedule_once(
            lambda dt: self.on_progress(value, status)
        )

    def run(self):
        try:
            print("=" * 80)
            print("DOWNLOAD STARTED")
            print("Platform     :", platform)
            print("Python       :", sys.version)
            print("yt-dlp       :", yt_dlp.version.__version__)
            print("URL          :", self.url)
            print("Format       :", self.format_id)
            print("Output Dir   :", self.download_dir)
            ffmpeg_path = get_ffmpeg_path()
            print("ffmpeg path  :", ffmpeg_path)

            try:
                result = subprocess.run(
                    [ffmpeg_path, "-version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                print("RETURN CODE :", result.returncode)
                print(result.stdout)

            except Exception:
                traceback.print_exc()

            print("=" * 80)

            opts = {
                "format": self.format_id,
                "outtmpl": os.path.join(
                    self.download_dir,
                    "%(title)s.%(ext)s"
                ),

                "progress_hooks": [self.progress_hook],
                "ffmpeg_location": ffmpeg_path,

                "windowsfilenames": platform == "win",
                "concurrent_fragment_downloads": 4,

                # Android debugging
                "quiet": True,
                "no_warnings": True,
                "logger": Logger(),
            }
            print("Creating YoutubeDL...")
            ydl = yt_dlp.YoutubeDL(opts)

            print("ffmpeg_location =", ydl.params.get("ffmpeg_location"))

            print("Starting download...")
            result = ydl.download([self.url])

            print("Download finished.")
            print("Result:", result)

            Clock.schedule_once(
                lambda dt: self.on_done()
            )

        except BaseException as e:
            print("=" * 80)
            print("DOWNLOAD FAILED")
            print("Exception:", repr(e))
            traceback.print_exc()
            print("=" * 80)

            error_message = str(e)
            def notify(dt):
                self.on_error(error_message)

            Clock.schedule_once(notify)

# ==================================================
# Themed UI primitives
# ==================================================
class Card(BoxLayout):
    """A BoxLayout with a rounded, themed background + border, matching
    gui.py's `QFrame#Card` / `QFrame#FormatCard` styling."""

    def __init__(self, bg=None, border=None, radius=14, border_width=1.2, **kwargs):
        super().__init__(**kwargs)
        self._radius = radius
        bg = bg or THEME["workspace"]
        border = border if border is not None else THEME["border"]

        with self.canvas.before:
            self._bg_color = Color(*get_color_from_hex(bg))
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
            self._border_color = Color(*get_color_from_hex(border)) if border else Color(0, 0, 0, 0)
            self._border_line = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, radius),
                width=border_width,
            )
        self.bind(pos=self._update, size=self._update)

    def _update(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, self._radius)

    def set_bg(self, hex_color):
        self._bg_color.rgba = get_color_from_hex(hex_color)

    def set_border(self, hex_color):
        self._border_color.rgba = get_color_from_hex(hex_color)

class RoundedProgressBar(Widget):
    """Rounded progress bar drawn with theme colors, mirroring gui.py's
    QProgressBar { background: interactive; } / ::chunk { background: accent; }."""

    def __init__(self, maximum=100, **kwargs):
        super().__init__(**kwargs)
        self.maximum = maximum
        self.value = 0
        with self.canvas:
            self._bg_color = Color(*get_color_from_hex(THEME["interactive"]))
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            self._chunk_color = Color(*get_color_from_hex(THEME["accent"]))
            self._chunk_rect = RoundedRectangle(pos=self.pos, size=(0, self.height), radius=[8])
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        ratio = (self.value / self.maximum) if self.maximum else 0
        w = max(0, min(self.width, self.width * ratio))
        self._chunk_rect.pos = self.pos
        self._chunk_rect.size = (w, self.height)

    def set_value(self, value):
        self.value = max(0, min(value, self.maximum))
        self._redraw()

def section_title(text, size=15):
    return Label(
        text=f"[b]{text}[/b]", markup=True, font_size=dp(size),
        halign="left", valign="middle", size_hint_y=None, height=dp(24),
        color=get_color_from_hex(THEME["text"]),
    )

def subtext_label(text, size=11, height=20):
    lbl = Label(
        text=text, font_size=dp(size), halign="left", valign="middle",
        size_hint_y=None, height=dp(height),
        color=get_color_from_hex(THEME["subtext"]),
    )
    lbl.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
    return lbl

# ==================================================
# Format card
# ==================================================
class FormatCard(ToggleButtonBehavior, Card):
    def __init__(self, fmt, on_select, **kwargs):
        super().__init__(
            group="formats", orientation="vertical",
            padding=(dp(12), dp(10)), spacing=dp(2),
            size_hint=(1, None), height=dp(92),
            bg=THEME["workspace"], border=THEME["border"], radius=12,
            **kwargs,
        )
        self.fmt = fmt
        self.on_select_cb = on_select

        quality = Label(
            text=f"[b]{fmt['quality']} \u2022 {fmt['extension']}[/b]", markup=True,
            font_size=dp(14), halign="left", valign="middle",
            size_hint_y=None, height=dp(22),
            color=get_color_from_hex(THEME["text"]),
        )
        quality.bind(size=lambda w, *_: setattr(w, "text_size", w.size))

        codec = Label(
            text=fmt["codec"].upper(), font_size=dp(11),
            halign="left", valign="middle", size_hint_y=None, height=dp(16),
            color=get_color_from_hex(THEME["subtext"]),
        )
        codec.bind(size=lambda w, *_: setattr(w, "text_size", w.size))

        size_lbl = Label(
            text=fmt["size"], font_size=dp(12), halign="left", valign="middle",
            size_hint_y=None, height=dp(18),
            color=get_color_from_hex(THEME["accent"]), bold=True,
        )
        size_lbl.bind(size=lambda w, *_: setattr(w, "text_size", w.size))

        self.add_widget(quality)
        self.add_widget(codec)
        self.add_widget(Widget())  # stretch, like gui.py's layout.addStretch()
        self.add_widget(size_lbl)

    def on_state(self, widget, value):
        if value == "down":
            self.set_bg(SELECTED_CARD_BG)
            self.set_border(THEME["accent"])
            self.on_select_cb(self.fmt)
        else:
            self.set_bg(THEME["workspace"])
            self.set_border(THEME["border"])

class FilterButton(ToggleButton):
    """Pill-style filter toggle standing in for gui.py's QRadioButton row."""

    def __init__(self, **kwargs):
        super().__init__(
            background_normal="", background_down="",
            color=get_color_from_hex(THEME["text"]),
            font_size=dp(12), **kwargs,
        )
        self.background_color = get_color_from_hex(THEME["interactive"])

    def on_state(self, widget, value):
        if value == "down":
            self.background_color = get_color_from_hex(THEME["accent"])
        else:
            self.background_color = get_color_from_hex(THEME["interactive"])

# ==================================================
# Root layout
# ==================================================
class TubitRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(16), spacing=dp(14), **kwargs)
        Window.clearcolor = get_color_from_hex(THEME["window"])

        self.download_dir = get_download_dir()
        self.all_formats = []
        self.selected_format = None
        self.video_info = None
        self.format_mode = "video"

        scroll = ScrollView(size_hint=(1, 1), bar_width=dp(4))
        self.content = BoxLayout(orientation="vertical", spacing=dp(14), size_hint_y=None, padding=(0, 0, 0, dp(8)))
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll.add_widget(self.content)
        self.add_widget(scroll)

        self._build_header()
        self._build_url_card()
        self._build_formats_card()
        self._build_info_card()
        self._build_download_card()

    # ---------- header ----------
    def _build_header(self):
        header = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(12))

        icon_path = resource_path(os.path.join("assets", "Tubit.png"))
        if os.path.exists(icon_path):
            logo = Image(source=icon_path, size_hint=(None, None), size=(dp(56), dp(56)))
        else:
            logo = Card(bg=THEME["accent"], border=None, radius=14,
                        size_hint=(None, None), size=(dp(56), dp(56)))
            logo.add_widget(Label(text="[b]T[/b]", markup=True, font_size=dp(26),
                                   color=get_color_from_hex(THEME["window"])))
        header.add_widget(logo)

        title_box = BoxLayout(orientation="vertical", spacing=dp(2))
        title = Label(
            text="[b]Video Downloader[/b]", markup=True, font_size=dp(20),
            halign="left", valign="bottom", size_hint_y=None, height=dp(30),
            color=get_color_from_hex(THEME["text"]),
        )
        title.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        subtitle = subtext_label("YouTube | Instagram \u2022 Fast \u2022 Simple \u2022 Reliable", size=11, height=28)

        title_box.add_widget(title)
        title_box.add_widget(subtitle)
        header.add_widget(title_box)

        self.content.add_widget(header)

    # ---------- URL card ----------
    def _build_url_card(self):
        card = Card(orientation="vertical", padding=dp(16), spacing=dp(8),
                    size_hint_y=None, height=dp(140))

        card.add_widget(section_title("\U0001F517 URL (YouTube | Instagram)", size=13))

        self.url_entry = TextInput(
            hint_text="Paste a video URL here...", multiline=False,
            size_hint_y=None, height=dp(44),
            background_color=get_color_from_hex(THEME["interactive"]),
            foreground_color=get_color_from_hex(THEME["text"]),
            hint_text_color=get_color_from_hex(THEME["subtext"]),
            cursor_color=get_color_from_hex(THEME["accent"]),
            padding=[dp(12), dp(12), dp(12), 0],
        )
        self.url_entry.bind(text=lambda *_: self._on_url_text_changed())

        self.fetch_btn = Button(
            text="Fetch Available Formats", size_hint_y=None, height=dp(44),
            background_normal="", background_color=get_color_from_hex(THEME["interactive"]),
            color=get_color_from_hex(THEME["subtext"]), bold=True,
            disabled=True,
        )
        self.fetch_btn.bind(on_release=lambda *_: self.fetch_formats())

        card.add_widget(self.url_entry)
        card.add_widget(self.fetch_btn)
        self.content.add_widget(card)

    def _on_url_text_changed(self):
        has_text = bool(self.url_entry.text.strip())
        self.fetch_btn.disabled = not has_text
        self.fetch_btn.background_color = get_color_from_hex(
            THEME["accent"] if has_text else THEME["interactive"]
        )
        self.fetch_btn.color = get_color_from_hex(
            "#FFFFFF" if has_text else THEME["subtext"]
        )
        if not has_text:
            self.video_title.text = "No video loaded"
            self.video_channel.text = "Channel : ---"
            self.video_duration.text = "Duration : --:--"
            self.thumbnail.source = ""

    # ---------- formats card ----------
    def _build_formats_card(self):
        card = Card(orientation="vertical", padding=dp(16), spacing=dp(8),
                    size_hint_y=None, height=dp(430))

        header_row = BoxLayout(size_hint_y=None, height=dp(24))
        header_row.add_widget(section_title("Available Formats", size=13))
        self.format_count = Label(
            text="0", size_hint_x=None, width=dp(30), font_size=dp(12),
            color=get_color_from_hex(THEME["subtext"]),
        )
        header_row.add_widget(self.format_count)
        card.add_widget(header_row)

        filter_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        self.video_btn = FilterButton(text="Video", group="mode", state="down")
        self.video_only_btn = FilterButton(text="Video Only", group="mode")
        self.audio_only_btn = FilterButton(text="Audio Only", group="mode")
        for btn in (self.video_btn, self.video_only_btn, self.audio_only_btn):
            btn.bind(on_release=lambda *_: self.filter_formats())
            filter_row.add_widget(btn)
        card.add_widget(filter_row)

        scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, padding=(0, dp(4)))
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll.add_widget(self.grid)
        card.add_widget(scroll)

        self.content.add_widget(card)

    # ---------- video info card ----------
    def _build_info_card(self):
        card = Card(orientation="vertical", padding=dp(16), spacing=dp(8),
                    size_hint_y=None, height=dp(150))

        card.add_widget(section_title("Video insights", size=13))

        info_row = BoxLayout(spacing=dp(10))
        self.thumbnail = AsyncImage(size_hint_x=None, width=dp(120))

        details = BoxLayout(orientation="vertical", spacing=dp(4))
        self.video_title = Label(
            text="No video loaded", font_size=dp(14), bold=True,
            halign="left", valign="top",
            color=get_color_from_hex(THEME["text"]),
        )
        self.video_title.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        self.video_channel = subtext_label("Channel : ---", size=11, height=18)
        self.video_duration = subtext_label("Duration : --:--", size=11, height=18)

        details.add_widget(self.video_title)
        details.add_widget(self.video_channel)
        details.add_widget(self.video_duration)

        info_row.add_widget(self.thumbnail)
        info_row.add_widget(details)
        card.add_widget(info_row)

        self.content.add_widget(card)

    # ---------- download card ----------
    def _build_download_card(self):
        card = Card(orientation="vertical", padding=dp(16), spacing=dp(6),
                    size_hint_y=None, height=dp(230))

        card.add_widget(section_title("Download", size=13))

        card.add_widget(subtext_label("Selected Format", size=10, height=16))
        self.selected_format_label = Label(
            text="No Format Selected", font_size=dp(14), bold=True,
            halign="left", valign="middle", size_hint_y=None, height=dp(22),
            color=get_color_from_hex(THEME["text"]),
        )
        self.selected_format_label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        card.add_widget(self.selected_format_label)

        self.download_btn = Button(
            text="Download", size_hint_y=None, height=dp(44), disabled=True,
            background_normal="", background_color=get_color_from_hex(THEME["interactive"]),
            color=get_color_from_hex(THEME["subtext"]), bold=True,
        )
        self.download_btn.bind(on_release=lambda *_: self.download_video())
        card.add_widget(self.download_btn)

        card.add_widget(subtext_label("Save", size=10, height=16))
        self.loc_label = Label(
            text=self.download_dir, font_size=dp(11), halign="left", valign="middle",
            size_hint_y=None, height=dp(20),
            color=get_color_from_hex(THEME["subtext"]),
        )
        self.loc_label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        card.add_widget(self.loc_label)

        self.progress = RoundedProgressBar(maximum=100, size_hint_y=None, height=dp(14))
        card.add_widget(self.progress)

        self.status_label = subtext_label("Select a format to continue.", size=11, height=18)
        card.add_widget(self.status_label)

        self.content.add_widget(card)

    # ==================================================
    # Behaviour
    # ==================================================
    def fetch_formats(self):
        url = self.url_entry.text.strip()
        if not url:
            return

        self.fetch_btn.disabled = True
        self.fetch_btn.text = "Fetching..."
        self.fetch_btn.background_color = get_color_from_hex(THEME["interactive"])
        self.fetch_btn.color = get_color_from_hex(THEME["subtext"])
        FetchWorker(url, self.populate_formats, self.on_error).start()

    def populate_formats(self, info, formats):
        self.all_formats = formats
        self.video_info = info

        self.fetch_btn.disabled = False
        self.fetch_btn.text = "Fetch Available Formats"
        self._on_url_text_changed()

        self.video_title.text = info.get("title", "Unknown")
        self.video_channel.text = f"Channel : {info.get('uploader', 'Unknown')}"
        self.video_duration.text = f"Duration : {info.get('duration_string', '--:--')}"
        self.thumbnail.source = info.get("thumbnail", "")

        self.selected_format = None
        self.selected_format_label.text = "No Format Selected"
        self.download_btn.disabled = True
        self.download_btn.background_color = get_color_from_hex(THEME["interactive"])
        self.download_btn.color = get_color_from_hex(THEME["subtext"])
        self.status_label.text = "Select a format to continue."

        self.filter_formats()

    def filter_formats(self):
        self.grid.clear_widgets()
        self.selected_format = None
        self.selected_format_label.text = "No Format Selected"
        self.download_btn.disabled = True
        self.download_btn.background_color = get_color_from_hex(THEME["interactive"])
        self.download_btn.color = get_color_from_hex(THEME["subtext"])

        if self.video_btn.state == "down":
            self.format_mode = "video"
            visible = [f for f in self.all_formats if f["has_video"]]
        elif self.video_only_btn.state == "down":
            self.format_mode = "video_only"
            visible = [f for f in self.all_formats if f["has_video"] and not f["has_audio"]]
        else:
            self.format_mode = "audio_only"
            visible = [f for f in self.all_formats if f["has_audio"] and not f["has_video"]]

        self.format_count.text = str(len(visible))

        if not visible:
            self.grid.add_widget(Label(
                text="No Formats Available.!", color=get_color_from_hex(THEME["subtext"]),
                size_hint_y=None, height=dp(40),
            ))
            return

        for fmt in visible:
            card = FormatCard(fmt, self.select_format, size_hint_x=0.5)
            self.grid.add_widget(card)

    def select_format(self, fmt):
        self.selected_format = fmt
        self.selected_format_label.text = f"\u2713 {fmt['quality']} \u2022 {fmt['extension']} \u2022 {fmt['size']}"
        self.download_btn.disabled = False
        self.download_btn.background_color = get_color_from_hex(THEME["accent"])
        self.download_btn.color = get_color_from_hex("#FFFFFF")

    def download_video(self):
        if not self.selected_format:
            return

        self.download_btn.disabled = True
        self.fetch_btn.disabled = True
        self.progress.set_value(0)
        self.status_label.text = "Starting download..."
        url = self.url_entry.text.strip()

        # --------------------------------------------
        # Build the format string
        # --------------------------------------------
        if self.format_mode == "video":
            format_id = (f"{self.selected_format['format_id']}+bestaudio/best")

        elif self.format_mode == "video_only":
            format_id = self.selected_format["format_id"]

        else:   # Audio Only
            format_id = self.selected_format["format_id"]

        DownloadWorker(
            url,
            format_id,
            self.download_dir,
            self.update_progress,
            self.download_complete,
            self.on_error,
        ).start()

    def update_progress(self, value, status):
        self.progress.set_value(value)
        self.status_label.text = status

    def download_complete(self):
        self.progress.set_value(100)
        self.download_btn.disabled = False
        self.download_btn.background_color = get_color_from_hex(THEME["accent"])
        self.download_btn.color = get_color_from_hex("#FFFFFF")
        self.fetch_btn.disabled = False
        self._on_url_text_changed()
        self.status_label.text = f"Saved to {self.download_dir}"
        Clock.schedule_once(lambda dt: self.progress.set_value(0), 1.5)

    def on_error(self, message):
        self.fetch_btn.disabled = False
        self._on_url_text_changed()
        self.fetch_btn.text = "Fetch Available Formats"
        self.download_btn.disabled = False
        self.status_label.text = f"Error: {message}"

class TubitApp(App):
    def build(self):
        self.title = "Tubit"
        return TubitRoot()


if __name__ == "__main__":
    TubitApp().run()