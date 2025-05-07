import pygame
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageDraw
import os
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.id3 import ID3
import io
import numpy as np
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
        "secondary": "#181818",
        "text": "#FFFFFF",
        "card": "#282828",
        "hover": "#333333",
        "progress_bg": "#535353",
        "progress_fg": "#1DB954"
    },
    "light": {
        "bg": "#FFFFFF",
        "primary": "#1DB954",
        "secondary": "#F5F5F5",
        "text": "#000000",
        "card": "#E0E0E0",
        "hover": "#EEEEEE",
        "progress_bg": "#D3D3D3",
        "progress_fg": "#1DB954"
    }
}

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify Premium Clone")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)
        
        # Variables de estado
        self.playlist = []
        self.current_song = 0
        self.playing = False
        self.dark_mode = True
        self.current_cover = None
        self.cover_img = None
        self.volume_level = 0.7
        self.search_query = tk.StringVar()
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Inicializar interfaz
        self.create_widgets()
        self.load_music()
        self.apply_theme()
        
        # Eventos de teclado
        self.root.bind("<space>", lambda e: self.play_pause())
        self.root.bind("<Right>", lambda e: self.next_song())
        self.root.bind("<Left>", lambda e: self.prev_song())
        self.root.bind("<Up>", lambda e: self.set_volume(min(1, self.volume_level + 0.1)))
        self.root.bind("<Down>", lambda e: self.set_volume(max(0, self.volume_level - 0.1)))
        
        # Iniciar actualizaciones
        self.update_progress()
        self.check_music_end()

    def configure_styles(self):
        self.style.configure('TFrame', background=THEME_COLORS["dark"]["bg"])
        
        self.style.configure('TLabel', 
                           background=THEME_COLORS["dark"]["bg"],
                           foreground=THEME_COLORS["dark"]["text"],
                           font=('Helvetica', 11))
        
        self.style.configure('Large.TLabel', 
                           font=('Helvetica', 16, 'bold'))
        
        self.style.configure('Small.TLabel', 
                           font=('Helvetica', 10))
        
        self.style.configure('TButton', 
                           background='transparent',
                           foreground=THEME_COLORS["dark"]["text"],
                           borderwidth=0,
                           font=('Helvetica', 11))
        
        self.style.map('TButton',
                      background=[('active', THEME_COLORS["dark"]["hover"])])
        
        self.style.configure('Treeview', 
                           background=THEME_COLORS["dark"]["card"],
                           foreground=THEME_COLORS["dark"]["text"],
                           fieldbackground=THEME_COLORS["dark"]["card"],
                           rowheight=35,
                           borderwidth=0)
        
        self.style.map('Treeview', 
                      background=[('selected', THEME_COLORS["dark"]["primary"])])
        
        self.style.configure('Horizontal.TProgressbar', 
                           background=THEME_COLORS["dark"]["progress_fg"],
                           troughcolor=THEME_COLORS["dark"]["progress_bg"])
        
        self.style.configure('TEntry',
                           fieldbackground=THEME_COLORS["dark"]["card"],
                           foreground=THEME_COLORS["dark"]["text"],
                           insertcolor=THEME_COLORS["dark"]["text"],
                           borderwidth=1,
                           relief='flat',
                           padding=5)

    def create_widgets(self):
        # Frame izquierdo (lista de canciones)
        self.left_frame = ttk.Frame(self.root, width=350)
        self.left_frame.pack(side="left", fill="both", padx=10, pady=10)

        # Barra de búsqueda
        search_frame = ttk.Frame(self.left_frame)
        search_frame.pack(fill="x", pady=(0, 10))

        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_query, style='TEntry')
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind('<KeyRelease>', lambda e: self.filter_songs())

        search_btn = ttk.Button(search_frame, text="🔍", style='TButton', command=self.filter_songs)
        search_btn.pack(side="right")

        # Lista de canciones
        self.songs_tree = ttk.Treeview(self.left_frame, columns=("Title", "Artist", "Album", "Duration"), show="headings")
        self.songs_tree.heading("Title", text="Título")
        self.songs_tree.heading("Artist", text="Artista")
        self.songs_tree.heading("Album", text="Álbum")
        self.songs_tree.heading("Duration", text="Duración")
        self.songs_tree.column("Title", width=150)
        self.songs_tree.column("Artist", width=120)
        self.songs_tree.column("Album", width=120)
        self.songs_tree.column("Duration", width=60)
        self.songs_tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.songs_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.songs_tree.configure(yscrollcommand=scrollbar.set)
        self.songs_tree.bind("<Double-1>", lambda e: self.play_song(self.songs_tree.index(self.songs_tree.selection()[0])))

        # Frame derecho (carátula y controles)
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Frame de la carátula
        cover_frame = ttk.Frame(self.right_frame)
        cover_frame.pack(fill="both", expand=True)

        self.cover_label = ttk.Label(cover_frame)
        self.cover_label.pack(pady=20)

        song_info_frame = ttk.Frame(cover_frame)
        song_info_frame.pack()

        self.song_title_label = ttk.Label(song_info_frame, style='Large.TLabel')
        self.song_title_label.pack()

        self.song_artist_label = ttk.Label(song_info_frame, style='Small.TLabel')
        self.song_artist_label.pack()

        # Controles
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100, 
                                      style='Horizontal.TProgressbar', mode='determinate')
        progress_bar.pack(fill="x", padx=20, pady=5)

        self.time_label = ttk.Label(control_frame, style='Small.TLabel')
        self.time_label.pack()

        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(pady=10)

        volume_frame = ttk.Frame(btn_frame)
        volume_frame.pack(side="left", padx=20)

        self.volume_slider = tk.Scale(volume_frame, from_=0, to=1, resolution=0.01, orient="horizontal",
                                    command=self.set_volume, showvalue=0, bg=THEME_COLORS["dark"]["bg"],
                                    troughcolor=THEME_COLORS["dark"]["secondary"],
                                    highlightthickness=0)
        self.volume_slider.set(self.volume_level)
        self.volume_slider.pack()

        player_btn_frame = ttk.Frame(btn_frame)
        player_btn_frame.pack(side="left", expand=True)

        self.prev_btn = ttk.Button(player_btn_frame, text="⏮", command=self.prev_song, style='TButton')
        self.prev_btn.pack(side="left", padx=5)

        self.play_btn = ttk.Button(player_btn_frame, text="▶", command=self.play_pause, style='TButton')
        self.play_btn.pack(side="left", padx=5)

        self.next_btn = ttk.Button(player_btn_frame, text="⏭", command=self.next_song, style='TButton')
        self.next_btn.pack(side="left", padx=5)

        self.theme_btn = ttk.Button(btn_frame, text="🌙", command=self.toggle_theme, style='TButton')
        self.theme_btn.pack(side="right", padx=20)

    # Resto de los métodos (load_music, extract_mp3_cover, extract_flac_cover, filter_songs, etc.)
    # ... (mantén todos los métodos anteriores pero con self. delante de las variables)
    
    def load_music(self):
        self.playlist = []
        self.songs_tree.delete(*self.songs_tree.get_children())
        
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
                        title = audio.get('TIT2', [os.path.splitext(file)[0]])[0]
                        artist = audio.get('TPE1', ['Unknown Artist'])[0]
                        album = audio.get('TALB', ['Unknown Album'])[0]
                        cover = self.extract_mp3_cover(audio)
                        
                    elif file.lower().endswith('.flac'):
                        audio = FLAC(filepath)
                        duration = audio.info.length
                        title = audio.get('title', [os.path.splitext(file)[0]])[0]
                        artist = audio.get('artist', ['Unknown Artist'])[0]
                        album = audio.get('album', ['Unknown Album'])[0]
                        cover = self.extract_flac_cover(audio)
                    
                    mins, secs = divmod(int(duration), 60)
                    duration_str = f"{mins}:{secs:02}"
                    
                    self.playlist.append({
                        "path": filepath,
                        "title": str(title),
                        "artist": str(artist),
                        "album": str(album),
                        "duration": duration,
                        "cover": cover
                    })
                    
                except Exception as e:
                    print(f"Error loading {file}: {e}")
        
        self.filter_songs()

    def extract_mp3_cover(self, audio):
        if 'APIC:' in audio.tags:
            cover_art = audio.tags['APIC:'].data
            return Image.open(io.BytesIO(cover_art))
        return None

    def extract_flac_cover(self, audio):
        if len(audio.pictures) > 0:
            cover_art = audio.pictures[0].data
            return Image.open(io.BytesIO(cover_art))
        return None

    def filter_songs(self):
        self.songs_tree.delete(*self.songs_tree.get_children())
        query = self.search_query.get().lower()
        
        for song in self.playlist:
            if (query in song['title'].lower() or 
                query in song['artist'].lower() or 
                query in song['album'].lower() or
                not query):
                
                mins, secs = divmod(int(song['duration']), 60)
                duration_str = f"{mins}:{secs:02}"
                self.songs_tree.insert("", "end", values=(song['title'], song['artist'], song['album'], duration_str))

    def update_cover(self):
        if self.playlist and self.current_song < len(self.playlist):
            song = self.playlist[self.current_song]
            if song["cover"]:
                img = song["cover"]
            else:
                img = Image.new('RGB', (300, 300), color='#121212')
                draw = ImageDraw.Draw(img)
                draw.text((100, 140), "No Cover", fill="white")
            
            # Aplicar bordes redondeados
            img = img.resize((300, 300), Image.LANCZOS)
            mask = Image.new('L', (300, 300), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse([(0, 0), (300, 300)], fill=255)
            
            result = Image.new('RGB', (300, 300), (25, 25, 25))
            result.paste(img, (0, 0), mask)
            
            # Añadir sombra
            shadow = Image.new('RGBA', (320, 320), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            for i in range(10, 0, -1):
                shadow_draw.ellipse([(i, i), (320-i, 320-i)], fill=(0, 0, 0, 10))
            
            final_img = Image.new('RGBA', (320, 320), (0, 0, 0, 0))
            final_img.paste(shadow, (0, 0), shadow)
            final_img.paste(result, (10, 10))
            
            self.cover_img = ImageTk.PhotoImage(final_img)
            self.cover_label.config(image=self.cover_img)
            self.cover_label.image = self.cover_img
            
            self.song_title_label.config(text=song['title'])
            self.song_artist_label.config(text=song['artist'])

    def play_pause(self):
        if not self.playlist:
            return
        
        if self.playing:
            pygame.mixer.music.pause()
            self.play_btn.config(text="▶")
            self.playing = False
        else:
            if pygame.mixer.music.get_busy() == 0:
                self.play_song(self.current_song)
            else:
                pygame.mixer.music.unpause()
            self.play_btn.config(text="⏸")
            self.playing = True

    def play_song(self, index):
        if 0 <= index < len(self.playlist):
            self.current_song = index
            pygame.mixer.music.load(self.playlist[self.current_song]["path"])
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(self.volume_level)
            self.playing = True
            self.play_btn.config(text="⏸")
            self.update_cover()
            self.highlight_song()

    def stop_music(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.play_btn.config(text="▶")

    def next_song(self):
        if self.playlist:
            self.play_song((self.current_song + 1) % len(self.playlist))

    def prev_song(self):
        if self.playlist:
            self.play_song((self.current_song - 1) % len(self.playlist))

    def highlight_song(self):
        for item in self.songs_tree.get_children():
            self.songs_tree.item(item, tags=("normal",))
        if self.playlist:
            items = self.songs_tree.get_children()
            if items and self.current_song < len(items):
                self.songs_tree.item(items[self.current_song], tags=("selected",))
                self.songs_tree.selection_set(items[self.current_song])
                self.songs_tree.see(items[self.current_song])

    def update_progress(self):
        if self.playing and self.playlist:
            current_time = pygame.mixer.music.get_pos() / 1000
            if current_time >= 0:
                self.progress_var.set(current_time)
                mins, secs = divmod(int(current_time), 60)
                total_mins, total_secs = divmod(int(self.playlist[self.current_song]["duration"]), 60)
                self.time_label.config(text=f"{mins}:{secs:02} / {total_mins}:{total_secs:02}")
        
        self.root.after(1000, self.update_progress)

    def seek_music(self, pos):
        if self.playing and self.playlist:
            pygame.mixer.music.set_pos(float(pos))

    def set_volume(self, val):
        self.volume_level = float(val)
        pygame.mixer.music.set_volume(self.volume_level)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        theme = THEME_COLORS["dark"] if self.dark_mode else THEME_COLORS["light"]
        
        # Configurar estilos
        self.style.configure('TFrame', background=theme["bg"])
        self.style.configure('TLabel', 
                           background=theme["bg"],
                           foreground=theme["text"])
        
        self.style.configure('Large.TLabel', 
                           foreground=theme["text"])
        
        self.style.configure('Small.TLabel', 
                           foreground=theme["text"])
        
        self.style.configure('TButton', 
                           background='transparent',
                           foreground=theme["text"])
        
        self.style.map('TButton',
                      background=[('active', theme["hover"])])
        
        self.style.configure('Treeview', 
                           background=theme["card"],
                           foreground=theme["text"],
                           fieldbackground=theme["card"])
        
        self.style.map('Treeview', 
                      background=[('selected', theme["primary"])])
        
        self.style.configure('Horizontal.TProgressbar', 
                           background=theme["progress_fg"],
                           troughcolor=theme["progress_bg"])
        
        self.style.configure('TEntry',
                           fieldbackground=theme["card"],
                           foreground=theme["text"],
                           insertcolor=theme["text"])
        
        # Configurar widgets
        self.root.config(bg=theme["bg"])
        self.volume_slider.config(bg=theme["bg"], troughcolor=theme["secondary"])
        
        self.theme_btn.config(text="☀️" if self.dark_mode else "🌙")
        
        if self.playlist and self.current_song < len(self.playlist):
            self.update_cover()

    def check_music_end(self):
        if self.playing and pygame.mixer.music.get_busy() == 0:
            self.next_song()
        self.root.after(1000, self.check_music_end)

# Crear y ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()