import subprocess as cmd
import platform
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading

def money_ape():
    print(r" __  __                              _                 ")
    print(r"|  \/  | ___  _ __   ___ _   _      / \   _ __   ___   ")
    print(r"| |\/| |/ _ \| '_ \ / _ \ | | |____/ _ \ | '_ \ / _ \  ")
    print(r"| |  | | (_) | | | |  __/ |_| |___/ ___ \| |_) |  __/  ")
    print(r"|_|  |_|\___/|_| |_|\___|\___,|  /_/   \_\ .__/ \___|  ")
    print(r"                         |___/           |_|           ")
    print("\033[1;32m\n                   Github : Money-Ape {verison : 1.1}")

money_ape()

current_os = platform.system()

def OS_platform_verify():

    os_var = current_os
    if os_var == "Windows":
        print(f"Platform Detected.! = {os_var}\n")
        module_names = ["yt_dlp", "tabulate", "PySide6"]
        for module_name in module_names:
            try:
                __import__(module_name)
                print(f"{module_name}.......ok")
                print(f"{module_name} is already installed.\n")

            except:
                print(f"{module_name}.......Error")
                print(f"{module_name} is not installed.\nInstalling...")
                try:
                    cmd.run(["cmd", "/c", "pip3", "install", module_name, "--quiet"])
                    print(f"{module_name} installed successfully.\n")
                except cmd.CalledProcessError:
                    print(f"Failed to install {module_name}.\n")
        
        # FFMPEG path for environment variable.!
        try:
            spath = r"ffmpeg"
            dpath = r"C:\\ffmpeg"
            cmd.run(["robocopy", spath, dpath, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/nc", "/ns", "/np"], check=True)
            cmd.run(["setx", "/M", "Path", f"%Path%;{dpath}\\bin" ], check=True)
            print("\033[1;32m[INFO] : ffmpeg installed successfully and path has been added to environment variable.!!")
        except cmd.CalledProcessError as e:
            print(f"\033[1;31m[ERROR]\033[0m: Command failed with exit code {e.returncode}\n")
            print("\033[1;31mThe Program should be executed with Administration.!\033[0m")
        except Exception as e:
            print(f"\033[1;33m[WARNING]\033[0m: {e}.!")
    
    elif os_var == "Linux":
        print(f"Platform Detected.! = {os_var}\n")
        module_names = ["yt_dlp", "tabulate", "tkinter"]
        for module_name in module_names:
            try:
                __import__(module_name)
                print(f"{module_name}.......ok")
                print(f"{module_name} is already installed.\n")
            except:
                print(f"{module_name}.......Error")
                print(f"{module_name} is not installed.\nInstalling...")
                try:
                    cmd.run(["pip", "install", module_name, "--quiet"])
                    print(f"{module_name} installed successfully.\n")
                except cmd.CalledProcessError:
                    print(f"Failed to install {module_name}.\n")
    else:
        print("Your Operating System isn't compatible for PYTUBE.!!")
OS_platform_verify()

import yt_dlp
from tabulate import tabulate

def format_file_size(size):
    if size is None:
        return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

def video_formats(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

        # Get ALL available formats with simplified details
        all_formats = []
        
        for fmt in formats:
            height = fmt.get('height')
            width = fmt.get('width')
            format_id = fmt['format_id']
            filesize = fmt.get('filesize_approx', fmt.get('filesize'))
            vcodec = fmt.get('vcodec', 'none')
            acodec = fmt.get('acodec', 'none')
            ext = fmt.get('ext', 'unknown')
            
            # Create format info with simplified display
            format_info = {
                'format_id': format_id,
                'height': height or 0,
                'width': width or 0,
                'filesize': format_file_size(filesize),
                'ext': ext.upper(),
                'has_video': vcodec != 'none',
                'has_audio': acodec != 'none',
                'vcodec': vcodec,
                'acodec': acodec
            }
            
            # Create simplified display name (only quality, size, extension)
            if height and vcodec != 'none':
                if acodec != 'none':
                    display_name = f"{height}p {ext.upper()}"
                else:
                    display_name = f"{height}p {ext.upper()}\n(Video Only)"
            elif acodec != 'none' and vcodec == 'none':
                display_name = f"Audio Only\n{ext.upper()}"
            else:
                display_name = f"Format {format_id}\n{ext.upper()}"
            
            format_info['display_name'] = display_name
            all_formats.append(format_info)
        
        # Sort formats: Video formats by resolution (desc), then audio formats
        video_formats = [f for f in all_formats if f['has_video']]
        audio_formats = [f for f in all_formats if not f['has_video'] and f['has_audio']]
        
        video_formats.sort(key=lambda x: x['height'], reverse=True)
        
        sorted_formats = video_formats + audio_formats
        
        return sorted_formats, info.get('title', 'Unknown Title')
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None
