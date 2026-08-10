#!/bin/bash
set -e

if [ ! -d ".venv" ]; then
    echo "[+] Virtual environment not found"
    echo "[+] Creating venv..."

    uv venv .venv --python 3.12
fi

# Activate .venv ONCE
echo "[+] Activating venv..."
source .venv/bin/activate

uv pip install yt-dlp kivy cython buildozer certifi pyjnius

# 4. Ask user
read -p "Clean build? (y/n): " build

if [[ "$build" =~ ^[Yy]$ ]]; then
    echo "[+] Cleaning old builds..."
    buildozer android clean
    rm -rf .buildozer
fi

# 5. Build (only once)
echo "[+] Building..."
buildozer -v android debug

# 6. Handle APK
APK=$(find bin -name "*-debug.apk" | head -n 1)

if [ -z "$APK" ]; then
    echo "[!] APK not found!"
    exit 1
fi

VERSION=$(grep "^version" buildozer.spec | cut -d'=' -f2 | tr -d ' ')

mv "$APK" "bin/tubit-$VERSION.apk"

echo "Final APK: bin/tubit-$VERSION.apk"