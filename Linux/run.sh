#!/usr/bin/bash

current_os=$(uname -s)

case "$current_os" in
	Linux)
		echo -e "\nOperating System is Linux.!"
		;;

	CYGWIN* | MINGW32* | MSYS* | MINGW*)
		echo -e "\nOperating system is Windows.!"
		;;
	*)
esac

modules=$(python - << 'EOF'
import importlib, sys

modules = ["yt_dlp", "tkinter", "tabulate"]
missing = []
for mod in modules:
	try:
		importlib.import_module(mod)
	except ImportError:
		missing.append(mod)
		print(f"\n{mod}.....missing")
print("\n")
if missing:
	sys.exit(1)
sys.exit(0)
EOF
)

modules_missing=$?

if [ -f /etc/os-release ]; then
	. /etc/os-release
	System_ID="$ID"

	echo -e "\nSystem : $System_ID[$NAME]\n"
	if [ "$System_ID" = "arch" ]; then
		if [ $modules_missing -ne 0 ]; then
			sudo pacman -Sy tk \
			python-tabulate \
			yt-dlp \
			ffmpeg
		else
			echo "Initializing....."
		fi
		
	elif [ "$System_ID" = "debian" ] || [ "$System_ID" = "ubuntu" ]; then
		if [ $modules_missing -ne 0 ]; then
			sudo apt-get update; sudo apt-get install yt_dlp \
			tk \
			python-tabulate \
			ffmpeg
		else
			echo "Intializing....."
		fi

	else
		echo "You ain't dumb than your machine.! right.?"
	fi
fi

python pytube.py
