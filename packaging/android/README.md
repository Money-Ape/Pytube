# 📱 Tubit

A Kivy-based Android video downloader powered by `yt-dlp` and `ffmpeg`, packaged using Buildozer and python-for-android.

---

## ⚠️ Important

This repository **does NOT include `buildozer.spec`**.

You must create and configure it manually before building.

---

## 🧰 Requirements

### Linux (Arch example)

```bash
sudo pacman -S python git zip unzip openjdk-17-jdk android-tools
pip install --upgrade buildozer cython
```

## 📦 Setup & Build

### 1. Initialize Buildozer

```bash
buildozer init
```

This creates:

```
buildozer.spec
```

### 2. Configure `buildozer.spec`

Replace its contents with:

```ini
[app]
title = Tubit
package.name = tubit
package.domain = org.moneyape

version = 1.4

source.dir = .
source.main = main.py
source.include_exts = py,png,jpg,jpeg,kv,ttf,json

requirements = python3,kivy,yt-dlp,certifi,pyjnius,ffmpeg

orientation = portrait
fullscreen = 0

p4a.local_recipes = ./p4a_recipes
p4a.source_dir = /<path_to_home_dir>/python-for-android

android.api = 35
android.minapi = 26
android.archs = arm64-v8a

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

icon.filename = assets/Tubit.png

# presplash.filename = assets/splash.png

[buildozer]
log_level = 2
warn_on_root = 1
```

### 3. Build APK

```bash
buildozer android debug
```

First build will take time (SDK + NDK download)

### 4. Install APK

```bash
adb install -r bin/*.apk
```

## 🧪 Debugging

```bash
adb logcat | grep python
```

## 🎬 FFmpeg Integration

FFmpeg is bundled via:

```ini
requirements = ..., ffmpeg
```

This produces:

```
libffmpegbin.so
```

inside the APK:

```
lib/arm64-v8a/libffmpegbin.so
```

### 🔧 Building Your Own FFmpeg Binary

The `libffmpegbin.so` consumed by `p4a.local_recipes` isn't built inside this repo — it comes from a separate pipeline: **[ffmpeg-android-native](https://github.com/Money-Ape/ffmpeg-android-native)**. Use it directly if you need to rebuild ffmpeg (e.g. a different codec set, a newer FFmpeg version, or a different target arch).

```bash
git clone https://github.com/Money-Ape/ffmpeg-android-native.git
cd ffmpeg-android-native
chmod +x *.sh
source ./env.sh          # points at Buildozer's NDK - run buildozer android debug once first if you haven't
./build.sh aarch64        # match Tubit's android.archs (arm64-v8a → aarch64 here)
```

This outputs:

```
ffmpeg-native-bin/ffmpeg-aarch64/ffmpeg
ffmpeg-native-bin/ffmpeg-aarch64/libffmpeg/libffmpegbin.so
```

Copy the `.so` into Tubit's local recipe so `p4a.local_recipes` picks it up on the next build:

```bash
cp ffmpeg-native-bin/ffmpeg-aarch64/libffmpeg/libffmpegbin.so \
   <path_to_Tubit>/p4a_recipes/ffmpeg/libffmpegbin.so
```

Then rebuild Tubit as usual:

```bash
buildozer android clean
buildozer android debug
```

**Keep the arch in sync:** if `buildozer.spec`'s `android.archs` ever changes from `arm64-v8a`, build the matching arch in `ffmpeg-android-native` too (`x86` for x86, `x86_64` for x86_64) — dropping one arch's binary into another arch's slot produces `Exec format error` at runtime on that device. See that repo's README for the full build/verify/packaging details, including why the binary has to ship as a native `.so` rather than an asset, and why the runtime symlink to it must live on internal storage.

## 📂 Storage Behavior

Downloads are handled safely:

1. Temporary download → app private storage
2. Final output →

```
/storage/emulated/0/Download/Tubit
```

Supports:

- Scoped Storage (Android 10+)
- MediaStore API
- Legacy permissions fallback

## 📁 Project Structure

```
.
├── main.py
├── gui.py
├── backend.py
├── theme.py
├── assets/
├── p4a_recipes/
└── buildozer.spec   (user-generated)
```

## ❗ Common Issues

**buildozer.spec missing**

```bash
buildozer init
```

**FFmpeg not working**

Ensure:

```
ffmpeg is included in requirements
```

If `libffmpegbin.so` itself is the problem (wrong arch, corrupted build, or you just want a fresher FFmpeg), rebuild it from **[ffmpeg-android-native](https://github.com/Money-Ape/ffmpeg-android-native)** — see the FFmpeg Integration section above.

**APK installs but crashes**

```bash
adb logcat | grep python
```

**File downloaded but not visible**

Check logs:

```bash
adb logcat
```

**Permission issues**

Handled automatically using:

- MediaStore (Android 10+)
- Runtime permissions (older Android)

## 🚀 Quick Build Flow

```bash
buildozer init
# edit buildozer.spec
buildozer android debug
adb install -r bin/*.apk
```

## ✅ Status

- ✔ Android build working
- ✔ FFmpeg bundled
- ✔ yt-dlp integrated
- ✔ Storage handling implemented