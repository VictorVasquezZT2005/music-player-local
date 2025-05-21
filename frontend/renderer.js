const { ipcRenderer } = require('electron');

const songListEl = document.getElementById('song-list');
const player = document.getElementById('player');

const coverImg = document.getElementById('cover');
const songTitle = document.getElementById('song-title');
const songArtist = document.getElementById('song-artist');
const songAlbum = document.getElementById('song-album');

ipcRenderer.on('music-list', (event, tracks) => {
  songListEl.innerHTML = '';

  if (tracks.length === 0) {
    songListEl.innerHTML = '<li style="padding: 15px; color:#999;">No se encontraron archivos .flac</li>';
    return;
  }

  tracks.forEach(track => {
    const li = document.createElement('li');
    li.classList.add('song-item');

    const img = document.createElement('img');
    img.classList.add('cover');
    img.src = track.picture || 'placeholder.png';

    const infoDiv = document.createElement('div');
    infoDiv.classList.add('song-info');

    infoDiv.innerHTML = `
      <strong>${track.title}</strong>
      <small>${track.artist}</small>
      <small>Álbum: ${track.album}</small>
    `;

    li.appendChild(img);
    li.appendChild(infoDiv);

    li.dataset.src = `../backend/media/${track.filename}`;

    songListEl.appendChild(li);
  });
});

songListEl.addEventListener('click', e => {
  const li = e.target.closest('li.song-item');
  if (!li) return;

  const currentActive = document.querySelector('li.song-item.active');
  if (currentActive) currentActive.classList.remove('active');
  li.classList.add('active');

  player.src = li.dataset.src;
  player.play();

  // Actualizar info en player
  coverImg.src = li.querySelector('img.cover').src;
  songTitle.textContent = li.querySelector('.song-info strong').textContent;
  songArtist.textContent = li.querySelectorAll('.song-info small')[0].textContent;
  songAlbum.textContent = li.querySelectorAll('.song-info small')[1].textContent;
});
