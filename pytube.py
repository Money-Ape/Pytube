import subprocess as cmd
import platform
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading

def money_ape():
    print("\033[1;93m                                   _          \033[0m")
    print("\033[1;93m|  \\/  | ___   _   ___            / \\   _   ___ \033[0m")
    print("\033[1;93m| |\\/| |/  \\| ' \\ /  \\ | | |____ /  \\ | ' \\ / _ \\\033[0m")
    print("\033[1;93m| |  | | (_) | | | |  __/ |_| |_____/ ___ \\| |_) |  __/\033[0m")
    print("\033[1;93m|_|  |_|\\___/|_| |_|\\___|\\__, |    /_/   \\_\\ .__/ \\___|\033[0m")
    print("\033[1;93m                         |___/             |_|\033[0m")
    print("\033[1;32m\n                    Github : Money-Ape\033[0m {verison : 1.0.0}\n")

money_ape()

current_os = platform.system()

def env_var_path():
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

def OS_platform_verify():
    global current_os
    if current_os == "Windows":
        print(f"Platform Detected.! = {current_os}\n")
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
                    cmd.run(["cmd", "/c", "pip3", "install", module_name, "--quiet"])
                    print(f"{module_name} installed successfully.\n")
                except cmd.CalledProcessError:
                    print(f"Failed to install {module_name}.\n")
    elif current_os == "Linux":
        print(f"Platform Detected.! = {current_os}\n")
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
                    cmd.run(["pip3", "install", module_name, "--quiet"])
                    print(f"{module_name} installed successfully.\n")
                except cmd.CalledProcessError:
                    print(f"Failed to install {module_name}.\n")
    else:
        print("This file isn't compatible on this system.!!")

env_var_path()
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

class Tubit:
    def __init__(self, root):
        self.root = root
        self.root.title("Money-Ape : Pytube")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(True, True)
        
        # Configure style for modern look
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors - Much darker theme
        self.bg_color = '#0d1117'
        self.card_color = '#161b22'
        self.input_bg = '#21262d'
        self.accent_color = '#238636'
        self.text_color = '#f0f6fc'
        self.muted_text = '#8b949e'
        self.border_color = '#30363d'
        self.selected_color = '#fd7e14'  # Orange for selected items
        
        # Download progress variables
        self.video_title = ""
        self.download_progress = 0
        self.selected_format = None
        self.all_formats = []
        self.format_buttons = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_frame = tk.Frame(header_frame, bg=self.bg_color)
        title_frame.pack()
        
        title_label = tk.Label(title_frame, text="Tubit",
                             font=('Arial', 28, 'bold'),
                             bg=self.bg_color, fg=self.text_color)
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(header_frame, text="Download YouTube videos - All available formats displayed",
                                font=('Arial', 12),
                                bg=self.bg_color, fg=self.muted_text)
        subtitle_label.pack(pady=(5, 0))
        
        # URL Input Section
        url_frame = tk.Frame(main_container, bg=self.card_color, relief=tk.FLAT, highlightbackground=self.border_color, highlightthickness=1)
        url_frame.pack(fill=tk.X, pady=(0, 15))
        
        url_inner = tk.Frame(url_frame, bg=self.card_color)
        url_inner.pack(fill=tk.X, padx=20, pady=20)
        
        url_label = tk.Label(url_inner, text="YouTube URL",
                           font=('Arial', 12, 'bold'),
                           bg=self.card_color, fg=self.text_color)
        url_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Center the URL input
        url_input_frame = tk.Frame(url_inner, bg=self.card_color)
        url_input_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.url_entry = tk.Entry(url_input_frame, font=('Arial', 12),
                                bg=self.input_bg, fg=self.text_color,
                                insertbackground=self.text_color,
                                relief=tk.FLAT, bd=0, justify='center',
                                highlightbackground=self.border_color, highlightthickness=1)
        self.url_entry.pack(fill=tk.X, ipady=12)
        
        # Center the fetch button
        button_frame = tk.Frame(url_inner, bg=self.card_color)
        button_frame.pack()
        
        self.fetch_button = tk.Button(button_frame, text="Fetch All Available Formats",
                                    command=self.fetch_formats_threaded,
                                    bg=self.accent_color, fg='white',
                                    font=('Arial', 12, 'bold'),
                                    relief=tk.FLAT, bd=0, cursor='hand2',
                                    activebackground='#2ea043', padx=25, pady=10)
        self.fetch_button.pack()
        
        # Quality Selection Section - Grid Layout (NO HORIZONTAL SCROLLBAR)
        quality_frame = tk.Frame(main_container, bg=self.card_color, highlightbackground=self.border_color, highlightthickness=1)
        quality_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        quality_inner = tk.Frame(quality_frame, bg=self.card_color)
        quality_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        quality_header = tk.Label(quality_inner, text="All Available Video Formats",
                                font=('Arial', 16, 'bold'),
                                bg=self.card_color, fg=self.text_color)
        quality_header.pack(pady=(0, 15))
        
        # Instructions
        instructions = tk.Label(quality_inner, text="Click 'Fetch All Available Formats' to see all downloadable options for this video",
                              font=('Arial', 11),
                              bg=self.card_color, fg=self.muted_text)
        instructions.pack(pady=(0, 20))
        
        # Create main scrollable area for grid layout (ONLY VERTICAL SCROLL)
        canvas = tk.Canvas(quality_inner, bg=self.card_color, highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(quality_inner, orient="vertical", command=canvas.yview)
        
        self.scrollable_frame = tk.Frame(canvas, bg=self.card_color)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set)
        
        # Pack scrollbar and canvas (NO HORIZONTAL SCROLLBAR)
        scrollbar_y.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Bottom section - Video Title and Download Controls
        bottom_frame = tk.Frame(main_container, bg=self.card_color, highlightbackground=self.border_color, highlightthickness=1)
        bottom_frame.pack(fill=tk.X)
        
        bottom_inner = tk.Frame(bottom_frame, bg=self.card_color)
        bottom_inner.pack(fill=tk.X, padx=20, pady=15)
        
        # Video Title Section
        video_title_label = tk.Label(bottom_inner, text="Video Title:",
                                   font=('Arial', 12, 'bold'),
                                   bg=self.card_color, fg=self.text_color)
        video_title_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Video title display with background
        video_title_container = tk.Frame(bottom_inner, bg=self.input_bg, highlightbackground=self.border_color, highlightthickness=1)
        video_title_container.pack(fill=tk.X, pady=(0, 15))
        
        self.video_title_display = tk.Label(video_title_container, text="No video selected",
                                          font=('Arial', 11),
                                          bg=self.input_bg, fg=self.muted_text,
                                          wraplength=600, justify=tk.LEFT, anchor='w')
        self.video_title_display.pack(fill=tk.X, padx=15, pady=10)
        
        # Download Section
        download_section = tk.Frame(bottom_inner, bg=self.card_color)
        download_section.pack(fill=tk.X, pady=(0, 15))
        
        # Selected format display
        selected_format_label = tk.Label(download_section, text="Selected Format:",
                                        font=('Arial', 12, 'bold'),
                                        bg=self.card_color, fg=self.text_color)
        selected_format_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.selected_format_display = tk.Label(download_section, text="No format selected",
                                               font=('Arial', 11),
                                               bg=self.card_color, fg=self.muted_text)
        self.selected_format_display.pack(anchor=tk.W, pady=(0, 15))
        
        # Download button
        download_button_frame = tk.Frame(download_section, bg=self.card_color)
        download_button_frame.pack()
        
        self.download_button = tk.Button(download_button_frame, text="Download Selected Format",
                                       command=self.download_video_threaded,
                                       bg=self.accent_color, fg='white',
                                       font=('Arial', 12, 'bold'),
                                       relief=tk.FLAT, bd=0, cursor='hand2',
                                       activebackground='#2ea043',
                                       padx=25, pady=10, state='disabled')
        self.download_button.pack()
        
        # Progress Section
        progress_section = tk.Frame(bottom_inner, bg=self.card_color)
        progress_section.pack(fill=tk.X, pady=(15, 0))
        
        # Progress bar section
        progress_label = tk.Label(progress_section, text="Download Progress:",
                                font=('Arial', 11, 'bold'),
                                bg=self.card_color, fg=self.text_color)
        progress_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Progress bar frame
        progress_bar_frame = tk.Frame(progress_section, bg=self.card_color)
        progress_bar_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Custom progress bar using Canvas
        self.progress_canvas = tk.Canvas(progress_bar_frame, height=20, bg=self.input_bg,
                                       highlightbackground=self.border_color, highlightthickness=1)
        self.progress_canvas.pack(fill=tk.X, side=tk.LEFT, padx=(0, 10))
        
        self.progress_text = tk.Label(progress_bar_frame, text="0%",
                                    font=('Arial', 10, 'bold'),
                                    bg=self.card_color, fg=self.text_color, width=6)
        self.progress_text.pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = tk.Label(progress_section, text="Ready to download",
                                   font=('Arial', 10),
                                   bg=self.card_color, fg=self.muted_text)
        self.status_label.pack(anchor=tk.W)
        
    def update_progress_bar(self, percentage):
        """Update the custom progress bar"""
        self.progress_canvas.delete("all")
        canvas_width = self.progress_canvas.winfo_width()
        canvas_height = self.progress_canvas.winfo_height()
        
        if canvas_width > 1:  # Make sure canvas is initialized
            progress_width = (canvas_width - 4) * (percentage / 100)
            
            # Background
            self.progress_canvas.create_rectangle(2, 2, canvas_width-2, canvas_height-2,
                                                fill=self.input_bg, outline="")
            
            # Progress fill
            if progress_width > 0:
                self.progress_canvas.create_rectangle(2, 2, progress_width+2, canvas_height-2,
                                                    fill=self.accent_color, outline="")
            
            # Update percentage text
            self.progress_text.config(text=f"{percentage:.1f}%")
    
    def create_format_grid(self):
        """Create format selection buttons in a grid layout with larger boxes"""
        # Clear existing buttons
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.format_buttons = []
        
        if not self.all_formats:
            no_formats_label = tk.Label(self.scrollable_frame,
                                      text="No formats available. Please fetch video information first.",
                                      font=('Arial', 12),
                                      bg=self.card_color, fg=self.muted_text)
            no_formats_label.pack(pady=20)
            return
        
        # Calculate grid dimensions - 4 columns for better layout
        columns = 4
        
        # Create grid
        current_row = 0
        current_col = 0
        
        for i, format_info in enumerate(self.all_formats):
            # Create button frame
            button_frame = tk.Frame(self.scrollable_frame, bg=self.card_color)
            button_frame.grid(row=current_row, column=current_col, padx=8, pady=8, sticky="ew")
            
            # Simplified format details for display (only quality, size, extension)
            display_text = format_info['display_name']
            if format_info['filesize'] != "Unknown":
                display_text += f"\n{format_info['filesize']}"
            
            # Larger quality button with increased size
            btn = tk.Button(button_frame, text=display_text,
                          command=lambda idx=i: self.select_format(idx),
                          bg=self.input_bg, fg=self.text_color,
                          font=('Arial', 11, 'bold'),  # Increased font size
                          relief=tk.FLAT, bd=0, cursor='hand2',
                          activebackground=self.accent_color,
                          activeforeground='white',
                          padx=20, pady=15,  # Increased padding for larger boxes
                          justify=tk.CENTER,
                          wraplength=180, width=18, height=4)  # Increased width and height
            btn.pack(fill=tk.BOTH, expand=True)
            
            self.format_buttons.append((btn, i))
            
            # Update grid position
            current_col += 1
            if current_col >= columns:
                current_col = 0
                current_row += 1
        
        # Configure grid weights for proper resizing
        for col in range(columns):
            self.scrollable_frame.grid_columnconfigure(col, weight=1, uniform="column")
    
    def select_format(self, format_index):
        """Select a format and update UI"""
        self.selected_format = self.all_formats[format_index]
        
        # Update button appearances
        for btn, idx in self.format_buttons:
            if idx == format_index:
                btn.config(bg=self.selected_color, fg='white')
            else:
                btn.config(bg=self.input_bg, fg=self.text_color)
        
        # Update selected format display
        display_text = self.selected_format['display_name']
        if self.selected_format['filesize'] != "Unknown":
            display_text += f" - {self.selected_format['filesize']}"
        
        self.selected_format_display.config(text=display_text, fg=self.text_color)
        
        # Enable download button
        self.download_button.config(state='normal')
    
    def fetch_formats_threaded(self):
        # Disable button and update status
        self.fetch_button.configure(state='disabled', text='Fetching All Formats...')
        self.status_label.config(text="Fetching all available video formats...")
        
        # Run in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.fetch_formats)
        thread.daemon = True
        thread.start()
    
    def fetch_formats(self):
        try:
            url = self.url_entry.get().strip()
            if not url:
                self.root.after(0, lambda: messagebox.showerror("Error", "Please enter a valid YouTube URL"))
                return
                
            all_formats, video_title = video_formats(url)
            if not all_formats:
                self.root.after(0, lambda: messagebox.showerror("Error", "No formats available or an error occurred."))
                return
            
            # Update UI in main thread
            self.root.after(0, lambda: self.update_format_display(all_formats, video_title))
            
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            # Re-enable button and update status
            self.root.after(0, lambda: self.fetch_button.configure(state='normal', text='Fetch All Available Formats'))
            self.root.after(0, lambda: self.status_label.config(text="Ready to download"))
    
    def update_format_display(self, all_formats, video_title):
        # Update video title
        self.video_title = video_title or "Unknown Title"
        self.video_title_display.config(text=self.video_title, fg=self.text_color)
        
        # Store all formats
        self.all_formats = all_formats
        
        # Create format grid
        self.create_format_grid()
        
        # Reset selection
        self.selected_format = None
        self.selected_format_display.config(text="No format selected", fg=self.muted_text)
        self.download_button.config(state='disabled')
        
        # Update status with format count
        self.status_label.config(text=f"Found {len(all_formats)} available formats")
    
    def download_video_threaded(self):
        if not self.selected_format:
            messagebox.showerror("Error", "Please select a format first")
            return
        
        # Disable button and update status
        self.download_button.configure(state='disabled', text='Downloading...')
        self.status_label.config(text="Starting download...")
        self.update_progress_bar(0)
        
        # Run in separate thread
        thread = threading.Thread(target=self.download_video)
        thread.daemon = True
        thread.start()
    
    def download_video(self):
        try:
            url = self.url_entry.get().strip()
            
            if not url or not self.selected_format:
                self.root.after(0, lambda: messagebox.showerror("Error", "Please enter URL and select format"))
                return
            
            # Get format ID for selected format
            format_id = self.selected_format['format_id']
            
            # Simulate progress updates
            for i in range(0, 101, 10):
                self.root.after(0, lambda p=i: self.update_progress_bar(p))
                self.root.after(0, lambda p=i: self.status_label.config(text=f"Downloading... {p}%"))
                threading.Event().wait(0.2)  # Simulated delay
            
            if current_os == "Windows":
                result = cmd.run(["cmd", "/c", "yt-dlp", "-f", f"{format_id}", f"{url}"],
                               capture_output=True, text=True)
            elif current_os == "Linux":
                result = cmd.run(["yt-dlp", "-f", f"{format_id}", f"{url}"],
                               capture_output=True, text=True)
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Unsupported platform"))
                return
            
            if result.returncode == 0:
                self.root.after(0, lambda: self.update_progress_bar(100))
                self.root.after(0, lambda: self.status_label.config(text="Download completed successfully!"))
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                    f"Video downloaded successfully!\n"
                    f"Format: {self.selected_format['display_name']}\n"
                    f"Size: {self.selected_format['filesize']}"))
            else:
                error_msg = result.stderr if result.stderr else "Download failed"
                self.root.after(0, lambda: self.status_label.config(text="Download failed"))
                self.root.after(0, lambda: messagebox.showerror("Download Error", error_msg))
                
        except Exception as e:
            error_msg = f"An error occurred during download: {str(e)}"
            self.root.after(0, lambda: self.status_label.config(text="Download error occurred"))
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            # Re-enable button
            self.root.after(0, lambda: self.download_button.configure(state='normal', text='Download Selected Format'))

if __name__ == "__main__":
    OS_platform_verify()
    
    root = tk.Tk()
    app = Tubit(root)
    root.mainloop()