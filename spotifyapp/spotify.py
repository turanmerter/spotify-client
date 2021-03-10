import json
import base64
import requests
import datetime

from spotifyapp.song import Song

class Spotify:
    # read spotify API credentials from this file
    _credential_file_name = "spotifyapp/credential.json"

    _access_token_url = "https://accounts.spotify.com/api/token"
    _search_url = "https://api.spotify.com/v1/search"
    _top_tracks_url= "https://api.spotify.com/v1/artists/{}/top-tracks"

    # keep spotify API credentials, ready to use
    _base64_credential = None
    # learn artist id for the first request, then keep it in memory
    _artist_id_dict = dict()
    _access_token = None
    # keep the time of expiration of the access token
    _expires_at = None
    # define a buffer (10% here) to prevent last second expirations
    # when making API calls
    _expiration_usage_perc = 0.9

    def read_credential(self):
        # reading from the environmant variables would be a better idea
        with open(self._credential_file_name, "r") as credential_file:
            credential = credential_file.read()
        credential_dictionary = json.loads(credential)
        credential_combined = credential_dictionary["client_id"] + ":" + credential_dictionary["client_secret"]
        self._base64_credential = base64.b64encode(credential_combined.encode("ascii")).decode("ascii")
    
    def _get_header_with_access_token(self):
        self._check_access_token()

        header = {"Authorization": "Bearer " + self._access_token}
        return header

    def _get_header_with_basic_auth(self):
        if self._base64_credential is None:
            self.read_credential()

        header = {"Authorization": "Basic " + self._base64_credential}
        return header

    def _get_access_token(self):
        body={"grant_type":"client_credentials"}
        response = requests.post(self._access_token_url, data=body, headers=self._get_header_with_basic_auth())
        if response.status_code != 200:
            raise Exception("Spotify returned an error for some reason")

        response_json = response.json()
        self._access_token = response_json["access_token"]
        expires_in = response_json["expires_in"]
        self._expires_at = datetime.datetime.now() + datetime.timedelta(0, int(expires_in * self._expiration_usage_perc)) 
    
    def _check_access_token(self):
        # for the first time
        if self._access_token is None or self._expires_at is None:
            self._get_access_token()
        # after expiration
        elif datetime.datetime.now() > self._expires_at:
            self._get_access_token()
    
    def _search_for_artist_id(self, artist_name):
        params={"q": artist_name, "type": "artist", "limit": 1}
        response = requests.get(self._search_url, params=params, headers=self._get_header_with_access_token())
        if response.status_code != 200:
            raise Exception("Spotify returned an error for some reason")

        response_json = response.json()
        self._artist_id_dict[artist_name] = self._parse_search_response(response_json)

    def _parse_search_response(self, response_json):
        artists = response_json.get("artists")
        if artists is None:
            raise Exception("Artist could not be found")

        items = artists.get("items")
        if artists is None:
            raise Exception("Artist could not be found")

        if len(items) <= 0:
            raise Exception("Artist could not be found")

        return items[0].get("id")

    def _get_artist_id(self, artist_name):
        if artist_name not in self._artist_id_dict:
            self._search_for_artist_id(artist_name)
        
        return self._artist_id_dict[artist_name]

    def get_most_popular_songs(self, artist_name):
        params={"market": "TR"} # just an assumption, can be configurable
        artist_id = self._get_artist_id(artist_name)
        response = requests.get(self._top_tracks_url.format(artist_id), params=params, headers=self._get_header_with_access_token())
        if response.status_code != 200:
            raise Exception("Spotify returned an error for some reason")

        response_json = response.json()

        return self._parse_most_popular_response(response_json)

    def _parse_most_popular_response(self, response_json):
        songs = list()

        songs_counter = 0
        tracks = response_json.get("tracks", [])
        for track in tracks:
            if songs_counter >= 5:
                break

            album = track.get("album")
            artists = track.get("artists", [])

            artist_name = "-"
            album_release_date = "unknown"
            album_image_url = ""
            track_name = track.get("name", "unknown")

            if len(artists) > 0:
                artist = artists[0]
                artist_name = artist.get("name", "-")
            
            if album is not None:
                album_release_date = album.get("release_date", "unknown")
                album_images = album.get("images")
                if album_images is not None:
                    if len(album_images) > 0:
                        album_image_url = album_images[0].get("url", "")

            songs.append(Song(artist_name, track_name, album_image_url, album_release_date).__dict__)
            songs_counter = songs_counter + 1

        return songs
