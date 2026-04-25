import pygame
from tkinter import *
from tkinter import filedialog
import time
import os

# --- Premium Configuration & Styling ---
BG_COLOR = "#0A0A0A"        # Deepest Black
ACCENT_COLOR = "#00F2FF"    # Neon Cyan
TEXT_COLOR = "#E0E0E0"      # Light Gray
SECONDARY_BG = "#1A1A1A"    # Dark Gray
HOVER_COLOR = "#00B4D8"     # Darker Cyan
PROGRESS_BG = "#333333"     # Progress bar background

root = Tk()
root.title("Aura MP3 Player")
root.geometry("600x600")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

pygame.mixer.init()

# --- Global Variables ---
song_length = 0
paused = False
song_start_pos = 0
is_dragging = False
playlist_paths = []
status_loop_id = None
current_vol = 0.7

# --- Core Functions ---

def add_song():
    song_path = filedialog.askopenfilename(initialdir='C:/', title='Choose A Song', filetypes=[("MP3 File", "*.mp3")])
    if song_path:
        song_name = os.path.basename(song_path).replace(".mp3", "")
        song_box.insert(END, f" 🎵 {song_name}")
        playlist_paths.append(song_path)

def add_folder():
    folder = filedialog.askdirectory(initialdir='C:/', title='Choose A Folder')
    if folder:
        for file in os.listdir(folder):
            if file.endswith(".mp3"):
                song_box.insert(END, f" 🎵 {file.replace('.mp3', '')}")
                playlist_paths.append(os.path.join(folder, file))

def play_song():
    global song_length, song_start_pos, paused
    try:
        current_selection = song_box.curselection()
        if not current_selection: 
            if song_box.size() > 0:
                song_box.selection_set(0)
                song_box.activate(0)
                current_selection = (0,)
            else:
                return

        idx = current_selection[0]
        song_path = playlist_paths[idx]
        
        song_name = os.path.basename(song_path).replace(".mp3", "")
        current_song_label.config(text=f"Playing: {song_name}")
        
        song_start_pos = 0
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(loops=0)
        paused = False
        
        song_sound = pygame.mixer.Sound(song_path)
        song_length = int(song_sound.get_length())
        
        play_btn.config(text="⏸" if not icons['pause'] else "", image=icons['pause']) # Switch to pause icon
        start_status_loop()
    except Exception as e:
        print(f"Error playing: {e}")

def pause_resume():
    global paused
    if not pygame.mixer.music.get_busy() and not paused:
        play_song()
        return

    if paused:
        pygame.mixer.music.unpause()
        paused = False
        play_btn.config(text="⏸" if not icons['pause'] else "", image=icons['pause'])
    else:
        pygame.mixer.music.pause()
        paused = True
        play_btn.config(text="▶" if not icons['play'] else "", image=icons['play'])

def next_song():
    try:
        current = song_box.curselection()
        if not current: return
        next_idx = (current[0] + 1) % song_box.size()
        
        song_box.selection_clear(0, END)
        song_box.activate(next_idx)
        song_box.selection_set(next_idx)
        play_song()
    except:
        pass

def prev_song():
    try:
        current = song_box.curselection()
        if not current: return
        prev_idx = (current[0] - 1) % song_box.size()
        
        song_box.selection_clear(0, END)
        song_box.activate(prev_idx)
        song_box.selection_set(prev_idx)
        play_song()
    except:
        pass

def seek_relative(seconds):
    global song_start_pos
    current_ms = pygame.mixer.music.get_pos()
    if current_ms == -1: return
    current_secs = song_start_pos + int(current_ms / 1000)
    new_pos = max(0, min(song_length, current_secs + seconds))
    song_start_pos = new_pos
    pygame.mixer.music.play(start=new_pos)
    if paused: pygame.mixer.music.pause()

def start_status_loop():
    global status_loop_id
    if status_loop_id:
        root.after_cancel(status_loop_id)
    status_loop_id = root.after(1000, update_status)

def update_status():
    global is_dragging, status_loop_id
    
    current_ms = pygame.mixer.music.get_pos()
    
    # Auto-play next logic
    if not pygame.mixer.music.get_busy() and not paused and song_length > 0:
        next_song()
        return

    if current_ms != -1:
        current_secs = song_start_pos + int(current_ms / 1000)
        
        if song_length > 0 and current_secs >= song_length:
            next_song()
            return

        if not is_dragging:
            draw_progress(current_secs)

        start_time = time.strftime("%M:%S", time.gmtime(current_secs))
        end_time = time.strftime("%M:%S", time.gmtime(song_length))
        time_label.config(text=f"{start_time} / {end_time}")
    
    status_loop_id = root.after(1000, update_status)

# --- Custom Canvas Widgets ---

def draw_progress(secs):
    progress_canvas.delete("bar")
    if song_length == 0: return
    width = progress_canvas.winfo_width()
    ratio = secs / song_length
    progress_canvas.create_rectangle(0, 0, width * ratio, 10, fill=ACCENT_COLOR, outline="", tags="bar")

def on_progress_click(event):
    global is_dragging, song_start_pos
    if song_length == 0: return
    width = progress_canvas.winfo_width()
    ratio = event.x / width
    song_start_pos = int(ratio * song_length)
    pygame.mixer.music.play(start=song_start_pos)
    if paused: pygame.mixer.music.pause()
    draw_progress(song_start_pos)

def set_volume(event):
    global current_vol
    width = volume_canvas.winfo_width()
    current_vol = max(0, min(1, event.x / width))
    pygame.mixer.music.set_volume(current_vol)
    draw_volume()

def draw_volume():
    volume_canvas.delete("vol")
    width = volume_canvas.winfo_width()
    volume_canvas.create_rectangle(0, 0, width * current_vol, 8, fill=ACCENT_COLOR, outline="", tags="vol")
    vol_percent_label.config(text=f"{int(current_vol * 100)}%")

# --- UI Layout ---

# Top Header
header_frame = Frame(root, bg=BG_COLOR)
header_frame.pack(fill=X, pady=20)
Label(header_frame, text="AURA MUSIC", font=("Helvetica", 24, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack()
current_song_label = Label(header_frame, text="Select a song to play", font=("Helvetica", 10), bg=BG_COLOR, fg=TEXT_COLOR)
current_song_label.pack(pady=5)

# Playlist Listbox
list_frame = Frame(root, bg=BG_COLOR)
list_frame.pack(fill=BOTH, expand=True, padx=40, pady=10)

song_box = Listbox(list_frame, bg=SECONDARY_BG, fg=TEXT_COLOR, borderwidth=0, highlightthickness=1, 
                   highlightbackground=PROGRESS_BG, selectbackground=ACCENT_COLOR, selectforeground="black",
                   font=("Helvetica", 11), height=10, activestyle="none")
song_box.pack(side=LEFT, fill=BOTH, expand=True)

scroll = Scrollbar(list_frame, orient=VERTICAL, command=song_box.yview)
scroll.pack(side=RIGHT, fill=Y)
song_box.config(yscrollcommand=scroll.set)

# Progress Area
progress_container = Frame(root, bg=BG_COLOR)
progress_container.pack(fill=X, padx=40, pady=10)

time_label = Label(progress_container, text="00:00 / 00:00", bg=BG_COLOR, fg=TEXT_COLOR, font=("Courier", 10))
time_label.pack(side=BOTTOM, pady=5)

progress_canvas = Canvas(progress_container, height=10, bg=PROGRESS_BG, highlightthickness=0, cursor="hand2")
progress_canvas.pack(fill=X)
progress_canvas.bind("<Button-1>", on_progress_click)

# Control Buttons
ctrl_frame = Frame(root, bg=BG_COLOR)
ctrl_frame.pack(pady=20)

def create_btn(cmd, icon_key=None, size=14):
    img = icons.get(icon_key) if icon_key else None
    btn = Button(ctrl_frame, text="" if not img else "", image=img, 
                  command=cmd, font=("Helvetica", size, "bold"), 
                  bg=BG_COLOR, fg=TEXT_COLOR, activebackground=SECONDARY_BG, 
                  activeforeground=ACCENT_COLOR, bd=0, padx=10, cursor="hand2")
    
    # Hover effects
    btn.bind("<Enter>", lambda e: btn.config(bg=SECONDARY_BG))
    btn.bind("<Leave>", lambda e: btn.config(bg=BG_COLOR))
    
    return btn

# Load icons using PhotoImage (Pure Tkinter)
def get_icon(path):
    try:
        img = PhotoImage(file=path)
        return img.subsample(2, 2)
    except:
        return None

icons = {
    'prev': get_icon('back.png'),
    'next': get_icon('forward.png'),
    'play': get_icon('play.png'),
    'pause': get_icon('pause.png'),
    'skip_f': get_icon('seek_forward_10.png'),
    'skip_b': get_icon('seek_back_10.png')
}

# Grid buttons with refined spacing
create_btn(prev_song, 'prev', 20).grid(row=0, column=0, padx=12)
create_btn(lambda: seek_relative(-10), 'skip_b').grid(row=0, column=1, padx=12)
play_btn = create_btn(pause_resume, 'play', 28)
play_btn.grid(row=0, column=2, padx=25)
create_btn(lambda: seek_relative(10), 'skip_f').grid(row=0, column=3, padx=12)
create_btn(next_song, 'next', 20).grid(row=0, column=4, padx=12)

# Volume Area
vol_frame = Frame(root, bg=BG_COLOR)
vol_frame.pack(pady=10)

Label(vol_frame, text="VOLUME", bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 8, "bold")).pack(side=LEFT, padx=10)
volume_canvas = Canvas(vol_frame, width=150, height=8, bg=PROGRESS_BG, highlightthickness=0, cursor="hand2")
volume_canvas.pack(side=LEFT)
volume_canvas.bind("<Button-1>", set_volume)
volume_canvas.bind("<B1-Motion>", set_volume)
vol_percent_label = Label(vol_frame, text="70%", bg=BG_COLOR, fg=ACCENT_COLOR, font=("Helvetica", 9, "bold"), width=4)
vol_percent_label.pack(side=LEFT, padx=10)

# Menu System
m_bar = Menu(root)
root.config(menu=m_bar)

file_m = Menu(m_bar, tearoff=0, bg=SECONDARY_BG, fg=TEXT_COLOR)
m_bar.add_cascade(label="Library", menu=file_m)
file_m.add_command(label="Add Song", command=add_song)
file_m.add_command(label="Add Folder", command=add_folder)
file_m.add_separator()
file_m.add_command(label="Clear Playlist", command=lambda: [song_box.delete(0, END), playlist_paths.clear()])

# Final Init
pygame.mixer.music.set_volume(0.7)
root.after(100, draw_volume) # Initial draw

root.mainloop()
