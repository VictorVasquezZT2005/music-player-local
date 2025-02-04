# Music Player Local

Reproductor de música minimalista en Python con `tkinter` y `pygame`.

## Requisitos

- **Python 3.11+** ([Descargar](https://www.python.org/downloads/))
- **Git** ([Descargar](https://git-scm.com/downloads))

## Instalación

### Windows
```sh
git clone https://github.com/VictorVasquezZT2005/music-player-local.git
cd music-player-local
pip install -r requirements.txt
pyinstaller --noconsole --onefile --icon=icon.ico music.py
```

### Linux (Debian y derivados)
```sh
sudo apt update && sudo apt install -y git python3-pip python3-tk
python3 -m pip install --break-system-packages pyinstaller

git clone https://github.com/VictorVasquezZT2005/music-player-local.git
cd music-player-local
pip install --break-system-packages -r requirements.txt
pyinstaller --noconsole --onefile --icon=icon.ico music.py
```

## Notas
- En **Linux**, `--break-system-packages` evita entornos virtuales.
- En **Windows**, asegúrate de que `pip` esté en el PATH.

![Preview](https://github.com/user-attachments/assets/6e067206-0650-425f-8bc3-3ebc81132bee) 🚀
