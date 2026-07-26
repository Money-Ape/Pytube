"""
Tubit - Android port (Kivy)

Ports the desktop PySide6 app (gui.py + tubit.py) to a single-file Kivy app
that can be packaged for Android with Buildozer.

Key differences from the desktop version, and why:

- No winreg / robocopy / Windows ffmpeg install: none of that exists on Android.
- No guaranteed system "ffmpeg" binary on a phone. Merging a separate
  video-only stream with a separate audio-only stream (the "1080p+bestaudio"
  trick the desktop app uses) needs ffmpeg. Rather than silently failing on
  device, this build only lists formats that already contain both video and
  audio in one stream ("progressive" formats), plus audio-only formats.
  If you bundle the p4a ffmpeg recipe and confirm a working `ffmpeg` binary
  is on PATH inside the app, you can re-enable merging (see
  ALLOW_STREAM_MERGE below).
- QThread/Signal -> threading.Thread + Clock.schedule_once, since Kivy
  widgets must only be touched from the main thread.
- QNetworkAccessManager thumbnail loading -> Kivy's AsyncImage widget.
- Native file dialog for choosing a download folder -> Android apps don't
  get an arbitrary folder picker without extra plugins, so this build
  downloads to the app's external storage "Download" folder automatically.

Packaging (buildozer.spec requirements, roughly):
    requirements = python3,kivy,yt-dlp,certifi,pyjnius,android
    android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

Run this file directly on a desktop with `python tubit_android.py` to test
the UI before building the APK; the android-only imports are skipped there.
"""

import os
import re
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.utils import get_color_from_hex, platform

import yt_dlp

from theme import THEMES

THEME = THEMES["blue_gray"]

# Flip to True only if you've bundled ffmpeg for Android and confirmed
# `shutil.which("ffmpeg")` actually resolves inside the packaged app.
ALLOW_STREAM_MERGE = False


# ==================================================
# Android storage / permissions helpers
# ==================================================
def get_download_dir():
    if platform == "android":
        try:
            from android.permissions import Permission, request_permissions
            from android.storage import primary_external_storage_path

            request_permissions([
                Permission.INTERNET,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
            ])

            download_dir = os.path.join(primary_external_storage_path(), "Download", "Tubit")
        except Exception as e:
            print(f"[Storage] falling back, could not resolve android storage: {e}")
            download_dir = os.path.join(os.path.expanduser("~"), "Tubit")
    else:
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Tubit")

    os.makedirs(download_dir, exist_ok=True)
    return download_dir


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
            opts = {"quiet": True, "skip_download": True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(self.url, download=False)

            formats = []
            seen = set()
            for fmt in info.get("formats", []):
                if not fmt.get("format_id"):
                    continue
                if fmt.get("protocol") == "mhtml":
                    continue

                height = fmt.get("height")
                vcodec = fmt.get("vcodec", "none")
                acodec = fmt.get("acodec", "none")
                filesize = fmt.get("filesize_approx", fmt.get("filesize"))

                has_video = vcodec != "none"
                has_audio = acodec != "none"

                # Without a guaranteed ffmpeg binary we can't merge separate
                # video-only + audio-only streams, so only expose formats
                # that are already usable as-is.
                if has_video and not has_audio and not ALLOW_STREAM_MERGE:
                    continue

                key = (height, fmt.get("ext"), vcodec, acodec)
                if key in seen:
                    continue
                seen.add(key)

                formats.append({
                    "format_id": fmt["format_id"],
                    "quality": f"{height}p" if height else "Audio",
                    "extension": fmt.get("ext", "Unknown").upper(),
                    "size": format_file_size(filesize),
                    "codec": vcodec if has_video else acodec,
                    "height": height or 0,
                    "has_audio": has_audio,
                    "has_video": has_video,
                })

            formats.sort(key=lambda x: (not x["has_video"], -x["height"]))
            Clock.schedule_once(lambda dt: self.on_done(info, formats))

        except Exception as e:
            Clock.schedule_once(lambda dt: self.on_error(str(e)))


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

        Clock.schedule_once(lambda dt: self.on_progress(value, status))

    def run(self):
        try:
            opts = {
                "format": self.format_id,
                "outtmpl": os.path.join(self.download_dir, "%(title)s.%(ext)s"),
                "progress_hooks": [self.progress_hook],
                "windowsfilenames": True,
                "concurrent_fragment_downloads": 4,
            }

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url])

            Clock.schedule_once(lambda dt: self.on_done())

        except Exception as e:
            Clock.schedule_once(lambda dt: self.on_error(str(e)))


# ==================================================
# UI helpers
# ==================================================
def bg_color_widget(widget, hex_color, radius=0):
    with widget.canvas.before:
        Color(*get_color_from_hex(hex_color))
        rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])

    def update(*_):
        rect.pos = widget.pos
        rect.size = widget.size

    widget.bind(pos=update, size=update)
    return rect


class FormatCard(ToggleButton):
    def __init__(self, fmt, on_select, **kwargs):
        super().__init__(group="formats", **kwargs)
        self.fmt = fmt
        self.on_select_cb = on_select
        self.markup = True
        self.halign = "left"
        self.valign = "middle"
        self.text_size = (dp(220), None)
        self.text = (
            f"[b]{fmt['quality']} - {fmt['extension']}[/b]\n"
            f"[size=11]{fmt['codec'].upper()}[/size]\n"
            f"[color=58A6FF]{fmt['size']}[/color]"
        )
        self.background_normal = ""
        self.background_down = ""
        self.background_color = get_color_from_hex(THEME["interactive"])
        self.color = get_color_from_hex(THEME["text"])
        self.size_hint_y = None
        self.height = dp(90)

    def on_state(self, widget, value):
        if value == "down":
            self.background_color = get_color_from_hex(THEME["selected"])
            self.on_select_cb(self.fmt)
        else:
            self.background_color = get_color_from_hex(THEME["interactive"])


class TubitRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(16), spacing=dp(10), **kwargs)
        Window.clearcolor = get_color_from_hex(THEME["window"])

        self.download_dir = get_download_dir()
        self.all_formats = []
        self.selected_format = None
        self.video_info = None

        self._build_header()
        self._build_url_row()
        self._build_info_row()
        self._build_format_filters()
        self._build_format_grid()
        self._build_download_row()

    # ---------- header ----------
    def _build_header(self):
        title = Label(
            text="[b]Tubit[/b]", markup=True, font_size=dp(28),
            size_hint_y=None, height=dp(40),
            color=get_color_from_hex(THEME["text"]),
        )
        subtitle = Label(
            text="YouTube | Instagram - Fast, Simple, Reliable",
            font_size=dp(13), size_hint_y=None, height=dp(24),
            color=get_color_from_hex(THEME["subtext"]),
        )
        self.add_widget(title)
        self.add_widget(subtitle)

    # ---------- URL entry ----------
    def _build_url_row(self):
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.url_entry = TextInput(
            hint_text="Paste a video URL...", multiline=False,
            background_color=get_color_from_hex(THEME["interactive"]),
            foreground_color=get_color_from_hex(THEME["text"]),
            padding=[dp(12), dp(12), 0, 0],
        )
        self.fetch_btn = Button(
            text="Fetch", size_hint_x=None, width=dp(100),
            background_normal="", background_color=get_color_from_hex(THEME["accent"]),
        )
        self.fetch_btn.bind(on_release=lambda *_: self.fetch_formats())
        row.add_widget(self.url_entry)
        row.add_widget(self.fetch_btn)
        self.add_widget(row)

    # ---------- video info + thumbnail ----------
    def _build_info_row(self):
        row = BoxLayout(size_hint_y=None, height=dp(120), spacing=dp(10))
        self.thumbnail = AsyncImage(size_hint_x=None, width=dp(160))

        info_box = BoxLayout(orientation="vertical", spacing=dp(4))
        self.video_title = Label(
            text="No video loaded", font_size=dp(15), halign="left", valign="top",
            color=get_color_from_hex(THEME["text"]),
        )
        self.video_title.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        self.video_channel = Label(
            text="", font_size=dp(12), halign="left", valign="top",
            color=get_color_from_hex(THEME["subtext"]),
        )
        self.video_channel.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        self.video_duration = Label(
            text="", font_size=dp(12), halign="left", valign="top",
            color=get_color_from_hex(THEME["subtext"]),
        )
        self.video_duration.bind(size=lambda w, *_: setattr(w, "text_size", w.size))

        info_box.add_widget(self.video_title)
        info_box.add_widget(self.video_channel)
        info_box.add_widget(self.video_duration)

        row.add_widget(self.thumbnail)
        row.add_widget(info_box)
        self.add_widget(row)

    # ---------- video / audio filter ----------
    def _build_format_filters(self):
        row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        self.video_btn = ToggleButton(text="Video", group="mode", state="down")
        self.audio_btn = ToggleButton(text="Audio Only", group="mode")
        self.video_btn.bind(on_release=lambda *_: self.filter_formats())
        self.audio_btn.bind(on_release=lambda *_: self.filter_formats())
        row.add_widget(self.video_btn)
        row.add_widget(self.audio_btn)
        self.add_widget(row)

    # ---------- formats grid ----------
    def _build_format_grid(self):
        scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, padding=dp(4))
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll.add_widget(self.grid)
        self.add_widget(scroll)

    # ---------- download row ----------
    def _build_download_row(self):
        self.selected_format_label = Label(
            text="No format selected", size_hint_y=None, height=dp(24),
            color=get_color_from_hex(THEME["subtext"]),
        )
        self.add_widget(self.selected_format_label)

        self.download_btn = Button(
            text="Download", size_hint_y=None, height=dp(48), disabled=True,
            background_normal="", background_color=get_color_from_hex(THEME["accent"]),
        )
        self.download_btn.bind(on_release=lambda *_: self.download_video())
        self.add_widget(self.download_btn)

        self.progress = ProgressBar(max=100, size_hint_y=None, height=dp(14))
        self.add_widget(self.progress)

        self.status_label = Label(
            text=f"Saving to: {self.download_dir}", size_hint_y=None, height=dp(24),
            color=get_color_from_hex(THEME["subtext"]),
        )
        self.add_widget(self.status_label)

    # ==================================================
    # Behaviour
    # ==================================================
    def fetch_formats(self):
        url = self.url_entry.text.strip()
        if not url:
            return

        self.fetch_btn.disabled = True
        self.fetch_btn.text = "Fetching..."
        FetchWorker(url, self.populate_formats, self.on_error).start()

    def populate_formats(self, info, formats):
        self.all_formats = formats
        self.video_info = info

        self.fetch_btn.disabled = False
        self.fetch_btn.text = "Fetch"

        self.video_title.text = info.get("title", "Unknown")
        self.video_channel.text = f"Channel: {info.get('uploader', 'Unknown')}"
        self.video_duration.text = f"Duration: {info.get('duration_string', '--:--')}"
        self.thumbnail.source = info.get("thumbnail", "")

        self.selected_format = None
        self.selected_format_label.text = "No format selected"
        self.download_btn.disabled = True

        self.filter_formats()

    def filter_formats(self):
        self.grid.clear_widgets()
        self.selected_format = None
        self.selected_format_label.text = "No format selected"
        self.download_btn.disabled = True

        if self.video_btn.state == "down":
            visible = [f for f in self.all_formats if f["has_video"]]
        else:
            visible = [f for f in self.all_formats if f["has_audio"] and not f["has_video"]]

        if not visible:
            self.grid.add_widget(Label(text="No formats available", color=get_color_from_hex(THEME["subtext"])))
            return

        for fmt in visible:
            card = FormatCard(fmt, self.select_format)
            self.grid.add_widget(card)

    def select_format(self, fmt):
        self.selected_format = fmt
        self.selected_format_label.text = f"Selected: {fmt['quality']} - {fmt['extension']} - {fmt['size']}"
        self.download_btn.disabled = False

    def download_video(self):
        if not self.selected_format:
            return

        self.download_btn.disabled = True
        self.fetch_btn.disabled = True
        self.progress.value = 0
        self.status_label.text = "Starting download..."

        url = self.url_entry.text.strip()
        DownloadWorker(
            url, self.selected_format["format_id"], self.download_dir,
            self.update_progress, self.download_complete, self.on_error,
        ).start()

    def update_progress(self, value, status):
        self.progress.value = value
        self.status_label.text = status

    def download_complete(self):
        self.progress.value = 100
        self.download_btn.disabled = False
        self.fetch_btn.disabled = False
        self.status_label.text = f"Saved to {self.download_dir}"

    def on_error(self, message):
        self.fetch_btn.disabled = False
        self.fetch_btn.text = "Fetch"
        self.download_btn.disabled = False
        self.status_label.text = f"Error: {message}"


class TubitApp(App):
    def build(self):
        self.title = "Tubit"
        return TubitRoot()


if __name__ == "__main__":
    TubitApp().run()