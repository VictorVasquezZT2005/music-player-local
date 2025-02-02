import pygame
import tkinter as tk
from tkinter import ttk
import os
from mutagen.mp3 import MP3
import time

# Inicializar pygame
pygame.mixer.init()

# Lista de reproducción
playlist = []
cancion_actual = 0
reproduciendo = False

# Función para cargar música automáticamente desde una carpeta
def cargar_musica_automaticamente():
    carpeta_musica = "musica"  # Nombre de la carpeta donde están los archivos de música
    if not os.path.exists(carpeta_musica):
        os.makedirs(carpeta_musica)
    
    archivos = [os.path.join(carpeta_musica, f) for f in os.listdir(carpeta_musica) if f.endswith(('.mp3', '.wav'))]
    for archivo in archivos:
        audio = MP3(archivo)
        duracion = int(audio.info.length)
        minutos, segundos = divmod(duracion, 60)
        duracion_formateada = f"{minutos}:{segundos:02}"
        playlist.append(archivo)
        lista_canciones.insert("", tk.END, values=(os.path.basename(archivo), duracion_formateada))

# Función para actualizar el botón de reproducción
def actualizar_boton():
    if reproduciendo:
        btn_reproducir.config(text="⏸️ Pausar")
    else:
        btn_reproducir.config(text="▶️ Reproducir")

# Función para reproducir o pausar la canción seleccionada
def reproducir_pausar():
    global reproduciendo
    if reproduciendo:
        pygame.mixer.music.pause()
        reproduciendo = False
    else:
        pygame.mixer.music.unpause()
        reproduciendo = True
    actualizar_boton()

# Función para detener la música
def detener_musica():
    global reproduciendo
    pygame.mixer.music.stop()
    reproduciendo = False
    actualizar_boton()

# Función para cambiar de canción
def cambiar_cancion(direccion):
    global cancion_actual, reproduciendo
    if playlist:
        cancion_actual = (cancion_actual + direccion) % len(playlist)
        pygame.mixer.music.load(playlist[cancion_actual])
        pygame.mixer.music.play()
        reproduciendo = True
        actualizar_boton()
        resaltar_cancion()
        actualizar_barra_progreso()

# Función para reproducir una canción al hacer doble clic
def seleccionar_cancion(event):
    global cancion_actual, reproduciendo
    if event.widget.identify_region(event.x, event.y) == "cell":
        seleccionado = lista_canciones.selection()
        if seleccionado:
            index = lista_canciones.index(seleccionado[0])
            cancion_actual = index
            pygame.mixer.music.load(playlist[cancion_actual])
            pygame.mixer.music.play()
            reproduciendo = True
            actualizar_boton()
            resaltar_cancion()
            actualizar_barra_progreso()

# Función para resaltar la canción seleccionada
def resaltar_cancion():
    for item in lista_canciones.get_children():
        lista_canciones.item(item, tags=("normal",))
    lista_canciones.item(lista_canciones.get_children()[cancion_actual], tags=("seleccionada",))

# Función para actualizar la barra de progreso
def actualizar_barra_progreso():
    if reproduciendo:
        tiempo_actual = pygame.mixer.music.get_pos() / 1000  # Obtener el tiempo en segundos
        barra_progreso["value"] = tiempo_actual
        ventana.after(1000, actualizar_barra_progreso)  # Actualizar cada segundo
        actualizar_tiempo_actual(tiempo_actual)

# Función para actualizar el tiempo actual de la canción
def actualizar_tiempo_actual(tiempo_actual):
    minutos, segundos = divmod(int(tiempo_actual), 60)
    tiempo_formateado = f"{minutos}:{segundos:02}"
    etiqueta_tiempo.config(text=tiempo_formateado)

# Función para cambiar manualmente el tiempo de la canción
def cambiar_tiempo_manual(valor):
    if playlist:
        tiempo_manual = int(float(valor))
        pygame.mixer.music.set_pos(tiempo_manual)
        actualizar_tiempo_actual(tiempo_manual)

# Crear ventana
ventana = tk.Tk()
ventana.title("Shēngzhí")
ventana.geometry("900x650")  # Tamaño inicial
ventana.configure(bg="#181818")  # Fondo oscuro

# Configurar pantalla completa
ventana.state("zoomed")  # Hace que la ventana inicie maximizada en Windows
# ventana.attributes('-fullscreen', True)  # Alternativa para pantalla completa sin bordes

# Estilos
style = ttk.Style()
style.theme_use('clam')  # Usar un tema más moderno

style.configure("Treeview", font=("Arial", 12), background="#181818", foreground="#FFFFFF", fieldbackground="#181818", rowheight=40)
style.configure("TButton", font=("Arial", 14), padding=10, background="#444444", foreground="#FFFFFF", relief="flat")
style.map("TButton", background=[("active", "#666666")])
style.map("Treeview", background=[("selected", "#666666")])
style.configure("Treeview.Heading", background="#222222", foreground="#FFFFFF", font=("Arial", 14, "bold"))

# Lista de canciones con columnas
frame_lista = tk.Frame(ventana, bg="#181818")
frame_lista.pack(pady=20, fill=tk.BOTH, expand=True)

# Agregar Scrollbar a la lista de canciones
scrollbar = tk.Scrollbar(frame_lista)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

lista_canciones = ttk.Treeview(frame_lista, columns=("Nombre", "Duración"), show="headings", selectmode="browse", yscrollcommand=scrollbar.set)
# Configurar encabezados de la tabla
lista_canciones.heading("Nombre", text="Nombre")
lista_canciones.heading("Duración", text="Duración")

# Configurar alineación del texto en las columnas
lista_canciones.column("Nombre", anchor="w")  # Alineado a la izquierda
lista_canciones.column("Duración", anchor="center")  # Centrado

lista_canciones.pack(fill=tk.BOTH, expand=True)

# Configurar el scrollbar
scrollbar.config(command=lista_canciones.yview)

# Agregar evento de doble clic para seleccionar canción
lista_canciones.bind("<Double-1>", seleccionar_cancion)

# Barra de progreso
frame_progreso = tk.Frame(ventana, bg="#181818")
frame_progreso.pack(pady=10, fill=tk.X)

barra_progreso = ttk.Scale(frame_progreso, from_=0, to=100, orient=tk.HORIZONTAL, command=cambiar_tiempo_manual)
barra_progreso.pack(fill=tk.X, padx=20)

# Etiqueta para mostrar el tiempo actual
etiqueta_tiempo = tk.Label(frame_progreso, text="0:00", bg="#181818", fg="#FFFFFF", font=("Arial", 12))
etiqueta_tiempo.pack(pady=5)

# Botones
frame_botones = tk.Frame(ventana, bg="#181818")
frame_botones.pack(pady=20)

btn_atras = ttk.Button(frame_botones, text="⏮️ Anterior", command=lambda: cambiar_cancion(-1))
btn_atras.grid(row=0, column=0, padx=15, pady=10)

btn_reproducir = ttk.Button(frame_botones, text="▶️ Reproducir", command=reproducir_pausar)
btn_reproducir.grid(row=0, column=1, padx=15, pady=10)

btn_siguiente = ttk.Button(frame_botones, text="⏭️ Siguiente", command=lambda: cambiar_cancion(1))
btn_siguiente.grid(row=0, column=2, padx=15, pady=10)

# Ajuste de los botones con más ancho
for widget in [btn_atras, btn_reproducir, btn_siguiente]:
    widget.config(width=15)  # Ajuste solo el ancho de los botones

# Personalización de las etiquetas seleccionadas
lista_canciones.tag_configure("seleccionada", background="#666666", foreground="#FFFFFF")

# Cargar música automáticamente al iniciar el programa
cargar_musica_automaticamente()

# Ejecutar ventana
ventana.mainloop()