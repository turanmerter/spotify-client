from flask import request, jsonify, render_template
from spotifyapp import app
import spotifyapp.service as service

@app.route('/genres', methods=['GET'])
def genres():
    genres = service.get_genres()
    return jsonify(genres)

@app.route('/tracks/<genre>', methods=['GET'])
def tracks(genre):
    songs = service.get_most_popular_songs(genre)
    return jsonify(songs)

@app.route('/')
def hello():
    return render_template('index.html', genre_list=service.get_genres())

try:
    # complete I/O heavy operations when starting the server
    # in case of exceptions, prevent server start
    service.initialize()
    if __name__ == "__main__":
        app.run()
    
except:
    print("Error occured during initialization")
