const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  getTracks: () => ipcRenderer.invoke('get-tracks')
});
