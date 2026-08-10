[app]
title = Tubit
package.name = tubit
package.domain = org.moneyape

version = 1.6

source.dir = .
source.main = main.py
source.include_exts = py,png,jpg,jpeg,kv,ttf,json
source.exclude_patterns = *.tmpl.py, tests/*, __pycache__/*

requirements = python3,kivy,yt-dlp,certifi,pyjnius,ffmpeg
orientation = portrait
fullscreen = 0

p4a.local_recipes = ./p4a_recipes
p4a.source_dir = /home/babayaga/Documents/DEV/python-for-android

android.api = 35
android.minapi = 26
android.archs = arm64-v8a, x86, x86_64
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

icon.filename = assets/Tubit.png
# presplash.filename = assets/splash.png

[buildozer]
log_level = 2
warn_on_root = 1