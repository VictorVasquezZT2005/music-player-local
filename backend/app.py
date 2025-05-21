import os
from flask import Flask, jsonify, send_from_directory
from mutagen.flac import FLAC

app = Flask(__name__)

MEDIA_FOLDER = os.path.join(os.path.dirname(__file__), 'media')
COVERS_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'covers')

@app.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory(MEDIA_FOLDER, filename)

@app.route('/static/covers/<path:filename>')
def serve_covers(filename):
    return send_from_directory(COVERS_FOLDER, filename)

@app.route('/tracks')
def list_tracks():
    tracks = []
    for file in os.listdir(MEDIA_FOLDER):
        if file.lower().endswith('.flac'):
            filepath = os.path.join(MEDIA_FOLDER, file)
            audio = FLAC(filepath)
            cover = None
            if audio.pictures:
                cover_name = file.replace('.flac', '.jpg')
                cover_path = os.path.join(COVERS_FOLDER, cover_name)
                if not os.path.exists(cover_path):
                    with open(cover_path, 'wb') as img_out:
                        img_out.write(audio.pictures[0].data)
                cover = cover_name
            tracks.append({
                'filename': file,
                'title': audio.get('title', ['Sin título'])[0],
                'artist': audio.get('artist', ['Desconocido'])[0],
                'album': audio.get('album', ['-'])[0],
                'cover': cover
            })
    return jsonify(tracks)

if __name__ == '__main__':
    app.run(debug=True)
