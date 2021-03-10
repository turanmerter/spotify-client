import json
import random

class Genres:
    _genres_file_name = "spotifyapp/genres.json"

    # keep genre to artists dictionary in memory
    _genre_dict = None

    def read_genres(self):
        if self._genre_dict is None:
            with open(self._genres_file_name) as genres_file:
                self._genre_dict = json.load(genres_file)
        
        return self._genre_dict
    
    # only user input (that can be validated) should be the genre name
    # we make the first read for genres json file in this method
    # so the earliest point we can control the input validity is here 
    def _get_artists(self, genre_name):
        if type(genre_name) != str or not genre_name:
            raise Exception("Given genre is not valid")

        genres = self.read_genres()
        if genre_name not in genres:
            raise Exception("Given genre is not in the list")

        artists = genres[genre_name]
        return artists
    
    def get_genres(self):
        return list(self.read_genres().keys())

    def select_artist_from_genre(self, genre_name):
        artists = self._get_artists(genre_name)
        artist_index = random.randint(0, len(artists) - 1)
        return artists[artist_index]