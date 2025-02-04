# Build Windows
https://www.python.org/downloads/
git clone https://github.com/VictorVasquezZT2005/music-player-local.git<br>
pip install -r requirements.txt<br>
pyinstaller --noconsole --onefile --icon=icon.ico music.py

# Build Linux
sudo apt update<br>
sudo apt install python3-pip -y<br>
git clone https://github.com/VictorVasquezZT2005/music-player-local.git<br>
pip install --break-system-packages -r requirements.txt<br>
pyinstaller --noconsole --onefile --icon=icon.ico music.py
