const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');
const mm = require('music-metadata');

async function getMusicData() {
  const mediaDir = path.join(__dirname, '..', 'backend', 'media');
  const files = fs.readdirSync(mediaDir).filter(f => f.endsWith('.flac'));

  const tracks = [];

  for (const file of files) {
    const filePath = path.join(mediaDir, file);
    try {
      const metadata = await mm.parseFile(filePath);
      const common = metadata.common;

      // Procesar carátula (si existe) en base64
      let pictureData = null;
      if (common.picture && common.picture.length > 0) {
        const pic = common.picture[0];
        const base64 = pic.data.toString('base64');
        pictureData = `data:${pic.format};base64,${base64}`;
      }

      tracks.push({
        filename: file,
        title: common.title || file,
        artist: common.artist || 'Desconocido',
        album: common.album || '-',
        picture: pictureData,
      });
    } catch (e) {
      console.error('Error leyendo metadata:', e);
      // Si falla, agrega solo el nombre del archivo
      tracks.push({
        filename: file,
        title: file,
        artist: 'Desconocido',
        album: '-',
        picture: null,
      });
    }
  }

  return tracks;
}

function createWindow() {
  const win = new BrowserWindow({
    width: 900,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    }
  });

  win.loadFile('index.html');

  win.webContents.on('did-finish-load', async () => {
    const tracks = await getMusicData();
    win.webContents.send('music-list', tracks);
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
