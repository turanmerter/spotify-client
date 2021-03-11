from spotifyapp.spotify import Spotify
from spotifyapp.genres import Genres

genres_service = Genres()
spotify_service = Spotify()

def initialize():
    genres_service.read_genres()
    spotify_service.read_credential()

def get_genres():
    try:
        genres = genres_service.get_genres()
        return genres
    except:
        return "Internal error"

def get_most_popular_songs(genre):
    artist = genres_service.select_artist_from_genre(genre)
    songs = spotify_service.get_most_popular_songs(artist)
    return songs