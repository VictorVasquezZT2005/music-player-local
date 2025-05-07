import pygame
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageOps, ImageDraw
import os
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.id3 import ID3
import io
import base64
import time

# Inicializar pygame
pygame.init()
pygame.mixer.init()

# Configuración
MUSIC_FOLDER = "media"
DEFAULT_COVER = "default_cover.png"
THEME_COLORS = {
    "dark": {
        "bg": "#121212",
        "primary": "#1DB954",
        "secondary": "#282828",
        "text": "#FFFFFF",
        "card": "#181818",
        "hover": "#333333",
        "progress_bg": "#535353",
        "progress_fg": "#1DB954"
    },
    "light": {
        "bg": "#F5F5F5",
        "primary": "#1DB954",
        "secondary": "#E0E0E0",
        "text": "#000000",
        "card": "#FFFFFF",
        "hover": "#EEEEEE",
        "progress_bg": "#D3D3D3",
        "progress_fg": "#1DB954"
    }
}

# Variables globales
playlist = []
current_song = 0
playing = False
dark_mode = True
current_cover = None
cover_img = None
volume_level = 0.7

# Crear ventana principal
root = tk.Tk()
root.title("Spotify Clone")
root.geometry("1100x700")
root.minsize(900, 600)
root.configure(bg=THEME_COLORS["dark"]["bg"])

# Estilo
style = ttk.Style()
style.theme_use('clam')

def configure_styles():
    style.configure('TFrame', background=THEME_COLORS["dark"]["bg"])
    
    style.configure('TLabel', 
                   background=THEME_COLORS["dark"]["bg"],
                   foreground=THEME_COLORS["dark"]["text"],
                   font=('Helvetica', 11))
    
    style.configure('Large.TLabel', 
                   font=('Helvetica', 14, 'bold'))
    
    style.configure('Small.TLabel', 
                   font=('Helvetica', 10))
    
    style.configure('TButton', 
                   background=THEME_COLORS["dark"]["secondary"],
                   foreground=THEME_COLORS["dark"]["text"],
                   borderwidth=0,
                   font=('Helvetica', 11))
    
    style.map('TButton',
              background=[('active', THEME_COLORS["dark"]["hover"])])
    
    style.configure('Treeview', 
                   background=THEME_COLORS["dark"]["card"],
                   foreground=THEME_COLORS["dark"]["text"],
                   fieldbackground=THEME_COLORS["dark"]["card"],
                   rowheight=35,
                   borderwidth=0)
    
    style.map('Treeview', 
              background=[('selected', THEME_COLORS["dark"]["primary"])])
    
    style.configure('Horizontal.TProgressbar', 
                   background=THEME_COLORS["dark"]["progress_fg"],
                   troughcolor=THEME_COLORS["dark"]["progress_bg"])

configure_styles()

# Funciones para manejar audio
def load_music():
    global playlist
    playlist = []
    songs_tree.delete(*songs_tree.get_children())
    
    if not os.path.exists(MUSIC_FOLDER):
        os.makedirs(MUSIC_FOLDER)
        return
    
    for file in os.listdir(MUSIC_FOLDER):
        if file.lower().endswith(('.mp3', '.flac', '.wav')):
            filepath = os.path.join(MUSIC_FOLDER, file)
            try:
                if file.lower().endswith('.mp3'):
                    audio = MP3(filepath, ID3=ID3)
                    duration = audio.info.length
                    # Extraer metadatos para MP3
                    title = audio.get('TIT2', ['Unknown'])[0]
                    artist = audio.get('TPE1', ['Unknown Artist'])[0]
                    album = audio.get('TALB', ['Unknown Album'])[0]
                    cover = extract_mp3_cover(audio)
                    
                elif file.lower().endswith('.flac'):
                    audio = FLAC(filepath)
                    duration = audio.info.length
                    # Extraer metadatos para FLAC
                    title = audio.get('title', ['Unknown'])[0]
                    artist = audio.get('artist', ['Unknown Artist'])[0]
                    album = audio.get('album', ['Unknown Album'])[0]
                    cover = extract_flac_cover(audio)
                
                mins, secs = divmod(int(duration), 60)
                duration_str = f"{mins}:{secs:02}"
                
                playlist.append({
                    "path": filepath,
                    "title": str(title),
                    "artist": str(artist),
                    "album": str(album),
                    "duration": duration,
                    "cover": cover
                })
                
                songs_tree.insert("", "end", values=(title, artist, album, duration_str))
                
            except Exception as e:
                print(f"Error loading {file}: {e}")

def extract_mp3_cover(audio):
    if 'APIC:' in audio.tags:
        cover_art = audio.tags['APIC:'].data
        return Image.open(io.BytesIO(cover_art))
    return None

def extract_flac_cover(audio):
    if len(audio.pictures) > 0:
        cover_art = audio.pictures[0].data
        return Image.open(io.BytesIO(cover_art))
    return None

def update_cover():
    global current_cover, cover_img
    
    if playlist and current_song < len(playlist):
        song = playlist[current_song]
        if song["cover"]:
            img = song["cover"]
        else:
            try:
                img = Image.new('RGB', (300, 300), color='#121212')
                draw = ImageDraw.Draw(img)
                draw.text((50, 120), "No Cover", fill="white")
            except:
                img = Image.new('RGB', (300, 300), color='#121212')
        
        # Aplicar bordes redondeados
        img = img.resize((300, 300), Image.LANCZOS)
        mask = Image.new('L', (300, 300), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([(0, 0), (300, 300)], fill=255)
        
        result = Image.new('RGB', (300, 300))
        result.paste(img, (0, 0), mask)
        
        cover_img = ImageTk.PhotoImage(result)
        cover_label.config(image=cover_img)
        cover_label.image = cover_img
        
        song_title_label.config(text=song['title'])
        song_artist_label.config(text=song['artist'])

def play_pause():
    global playing
    if not playlist:
        return
    
    if playing:
        pygame.mixer.music.pause()
        play_btn.config(text="▶")
        playing = False
    else:
        if pygame.mixer.music.get_busy() == 0:
            play_song(current_song)
        else:
            pygame.mixer.music.unpause()
        play_btn.config(text="⏸")
        playing = True

def play_song(index):
    global current_song, playing
    if 0 <= index < len(playlist):
        current_song = index
        pygame.mixer.music.load(playlist[current_song]["path"])
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(volume_level)
        playing = True
        play_btn.config(text="⏸")
        update_cover()
        update_progress()
        highlight_song()

def stop_music():
    global playing
    pygame.mixer.music.stop()
    playing = False
    play_btn.config(text="▶")

def next_song():
    if playlist:
        play_song((current_song + 1) % len(playlist))

def prev_song():
    if playlist:
        play_song((current_song - 1) % len(playlist))

def highlight_song():
    for item in songs_tree.get_children():
        songs_tree.item(item, tags=("normal",))
    if playlist:
        items = songs_tree.get_children()
        if items and current_song < len(items):
            songs_tree.item(items[current_song], tags=("selected",))
            songs_tree.selection_set(items[current_song])
            songs_tree.see(items[current_song])

def update_progress():
    if playing and playlist:
        current_time = pygame.mixer.music.get_pos() / 1000
        if current_time >= 0:
            progress_var.set(current_time)
            mins, secs = divmod(int(current_time), 60)
            total_mins, total_secs = divmod(int(playlist[current_song]["duration"]), 60)
            time_label.config(text=f"{mins}:{secs:02} / {total_mins}:{total_secs:02}")
    
    root.after(1000, update_progress)

def seek_music(pos):
    if playing and playlist:
        pygame.mixer.music.set_pos(float(pos))

def set_volume(val):
    global volume_level
    volume_level = float(val)
    pygame.mixer.music.set_volume(volume_level)

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()

def apply_theme():
    theme = THEME_COLORS["dark"] if dark_mode else THEME_COLORS["light"]
    
    style.configure('TFrame', background=theme["bg"])
    style.configure('TLabel', 
                   background=theme["bg"],
                   foreground=theme["text"])
    
    style.configure('Large.TLabel', 
                   foreground=theme["text"])
    
    style.configure('Small.TLabel', 
                   foreground=theme["text"])
    
    style.configure('TButton', 
                   background=theme["secondary"],
                   foreground=theme["text"])
    
    style.map('TButton',
              background=[('active', theme["hover"])])
    
    style.configure('Treeview', 
                   background=theme["card"],
                   foreground=theme["text"],
                   fieldbackground=theme["card"])
    
    style.map('Treeview', 
              background=[('selected', theme["primary"])])
    
    style.configure('Horizontal.TProgressbar', 
                   background=theme["progress_fg"],
                   troughcolor=theme["progress_bg"])
    
    root.config(bg=theme["bg"])
    lyrics_display.config(bg=theme["bg"], fg=theme["text"])
    volume_slider.config(bg=theme["bg"], troughcolor=theme["secondary"])
    
    theme_btn.config(text="☀️" if dark_mode else "🌙")
    
    if playlist and current_song < len(playlist):
        update_cover()

# Interfaz de usuario
# Frame izquierdo (lista de canciones)
left_frame = ttk.Frame(root, width=350)
left_frame.pack(side="left", fill="both", padx=10, pady=10)

search_frame = ttk.Frame(left_frame)
search_frame.pack(fill="x", pady=5)

search_entry = ttk.Entry(search_frame, style='TEntry')
search_entry.pack(side="left", fill="x", expand=True)

search_btn = ttk.Button(search_frame, text="Buscar", style='TButton')
search_btn.pack(side="right")

songs_tree = ttk.Treeview(left_frame, columns=("Title", "Artist", "Album", "Duration"), show="headings")
songs_tree.heading("Title", text="Título")
songs_tree.heading("Artist", text="Artista")
songs_tree.heading("Album", text="Álbum")
songs_tree.heading("Duration", text="Duración")
songs_tree.column("Title", width=150)
songs_tree.column("Artist", width=120)
songs_tree.column("Album", width=120)
songs_tree.column("Duration", width=60)
songs_tree.pack(fill="both", expand=True)

scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=songs_tree.yview)
scrollbar.pack(side="right", fill="y")
songs_tree.configure(yscrollcommand=scrollbar.set)

# Frame derecho (carátula y controles)
right_frame = ttk.Frame(root)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# Frame de la carátula
cover_frame = ttk.Frame(right_frame)
cover_frame.pack(fill="both", expand=True, pady=20)

cover_label = ttk.Label(cover_frame)
cover_label.pack()

song_info_frame = ttk.Frame(cover_frame)
song_info_frame.pack(pady=10)

song_title_label = ttk.Label(song_info_frame, style='Large.TLabel')
song_title_label.pack()

song_artist_label = ttk.Label(song_info_frame, style='Small.TLabel')
song_artist_label.pack()

# Frame de letras
lyrics_frame = ttk.Frame(right_frame)
lyrics_frame.pack(fill="both", expand=True)

lyrics_display = tk.Label(lyrics_frame, font=("Helvetica", 12), justify="center", wraplength=400)
lyrics_display.pack(fill="both", expand=True)

# Controles
control_frame = ttk.Frame(root)
control_frame.pack(side="bottom", fill="x", padx=10, pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(control_frame, variable=progress_var, maximum=100, 
                              style='Horizontal.TProgressbar', mode='determinate')
progress_bar.pack(fill="x", padx=20, pady=5)

time_label = ttk.Label(control_frame, style='Small.TLabel')
time_label.pack()

btn_frame = ttk.Frame(control_frame)
btn_frame.pack(pady=10)

volume_frame = ttk.Frame(btn_frame)
volume_frame.pack(side="left", padx=20)

volume_slider = tk.Scale(volume_frame, from_=0, to=1, resolution=0.01, orient="horizontal",
                        command=set_volume, showvalue=0, bg=THEME_COLORS["dark"]["bg"],
                        troughcolor=THEME_COLORS["dark"]["secondary"],
                        highlightthickness=0)
volume_slider.set(volume_level)
volume_slider.pack()

player_btn_frame = ttk.Frame(btn_frame)
player_btn_frame.pack(side="left", expand=True)

prev_btn = ttk.Button(player_btn_frame, text="⏮", command=prev_song, style='TButton')
prev_btn.pack(side="left", padx=5)

play_btn = ttk.Button(player_btn_frame, text="▶", command=play_pause, style='TButton')
play_btn.pack(side="left", padx=5)

next_btn = ttk.Button(player_btn_frame, text="⏭", command=next_song, style='TButton')
next_btn.pack(side="left", padx=5)

theme_btn = ttk.Button(btn_frame, text="🌙", command=toggle_theme, style='TButton')
theme_btn.pack(side="right", padx=20)

# Eventos
songs_tree.bind("<Double-1>", lambda e: play_song(songs_tree.index(songs_tree.selection()[0])))
root.bind("<space>", lambda e: play_pause())
root.bind("<Right>", lambda e: next_song())
root.bind("<Left>", lambda e: prev_song())
root.bind("<Up>", lambda e: set_volume(min(1, volume_level + 0.1)))
root.bind("<Down>", lambda e: set_volume(max(0, volume_level - 0.1)))

# Inicialización
load_music()
apply_theme()

def check_music_end():
    if playing and pygame.mixer.music.get_busy() == 0:
        next_song()
    root.after(1000, check_music_end)

check_music_end()
update_progress()

root.mainloop()