# Music Player Local

Este proyecto es un reproductor de música minimalista desarrollado en Python con `tkinter` y `pygame`. A continuación, se explican los pasos para compilarlo en **Windows** y **Linux**.

## Requisitos

- **Python 3.11 o superior** ([Descargar aquí](https://www.python.org/downloads/))
- **Git** instalado en tu sistema

## Compilación en Windows

```sh
# Descargar e instalar Python desde el sitio oficial
https://www.python.org/downloads/

# Clonar el repositorio
git clone https://github.com/VictorVasquezZT2005/music-player-local.git
cd music-player-local

# Instalar dependencias
pip install -r requirements.txt

# Crear el ejecutable
pyinstaller --noconsole --onefile --icon=icon.ico music.py
```

## Compilación en Linux (Debian y derivados)

```sh
# Actualizar paquetes del sistema
sudo apt update

# Instalar pip y dependencias necesarias
sudo apt install python3-pip -y
python3 -m pip install --break-system-packages pyinstaller
sudo apt install python3-tk -y

# Clonar el repositorio
git clone https://github.com/VictorVasquezZT2005/music-player-local.git
cd music-player-local

# Instalar dependencias del proyecto
pip install --break-system-packages -r requirements.txt

# Crear el ejecutable
pyinstaller --noconsole --onefile --icon=icon.ico music.py
```

## Notas
- En **Linux**, se usa `--break-system-packages` para instalar dependencias sin un entorno virtual.
- En **Windows**, asegúrate de que `pip` esté en el PATH al instalar Python.

Con estos pasos, deberías poder compilar el proyecto sin problemas. 🚀

