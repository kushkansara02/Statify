import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotipyClient(object):
    # class properties
    username = None
    client_id = None
    client_secret = None
    redirect_uri = "https://google.ca/"
    spotify_obj = None

    # this is just for reference
    scopes = {"images": "ugc-image-upload", "read_playback": "user-read-playback-state",
              "modify_playback": "user-modify-playback-state", "currently_playing": "user-read-currently-playing",
              "user_email": "user-read-email", "account_type": "user-read-private",
              "collab_playlists": "playlist-read-collaborative",
              "write_access_public_playlist": "playlist-modify-public",
              "read_access_private_playlists": "playlist-read-private",
              "write_access_private_playlist": "playlist-modify-private", "library_write_access": "user-library-modify",
              "library_read_access": "user-library-read", "top_read": "user-top-read",
              "playback_position": "user-read-playback-position", "recently_played": "user-read-recently-played",
              "follows_read": "user-follow-read", "follows_access": "user-follow-modify"}
    all_scopes = ""

    for val in scopes.values():
        all_scopes += f"{val} "

    # getting the scopes in array form
    all_scopes = all_scopes[:-1]

    def __init__(self, username, client_id, client_secret):
        # initializing all variables needed
        self.username = username
        self.client_id = client_id
        self.client_secret = client_secret
        self.createSpotifyObj()

    def createSpotifyObj(self):
        # performs authentication for user and obtains the Spotipy object
        self.spotify_obj = spotipy.Spotify(
            client_credentials_manager=SpotifyOAuth(client_id=self.client_id, client_secret=self.client_secret,
                                                    scope=self.all_scopes))

    def getUserPlaylists(self):
        # returns all user playlists { {"name":"id"}, ... }
        playlists = self.spotify_obj.user_playlists(self.username)
        playlist_info = {}

        for playlist in playlists["items"]:
            playlist_info[playlist["name"]] = playlist["id"]

        return playlist_info

    def getUserShows(self):
        # returns all user followed podcasts/shows { {"name":"id"}, ... }
        shows = self.spotify_obj.current_user_saved_shows()
        show_info = {}

        for show in shows["items"]:
            show_info[show["show"]["name"]] = show["show"]["id"]

        return show_info

    def addShows(self, shows):
        # takes show ids as inputs and follows them for the user
        self.spotify_obj.current_user_saved_shows_add(shows=shows)

    def get_playlist_tracks(self, playlist_id):
        # gets all the tracks within a playlist { {"name":"id"}, ... }
        # extra steps necessary because request limit for the method is 100

        results = self.spotify_obj.user_playlist_tracks(self.username, playlist_id)
        tracks = results['items']
        track_info = {}

        while results['next']:
            results = self.spotify_obj.next(results)
            tracks.extend(results['items'])

        for x in range(results["total"]):
            track_info[tracks[x]["track"]["name"]] = tracks[x]["track"]["id"]

        return track_info

    def addTracks(self, playlist_id, tracks):
        # adds given tracks based on track ids onto a playlist
        # assuming the tracks are given in a dict: { {"name":"id}, ... }

        tracks_id = []

        for track_id in tracks.values():
            tracks_id.append(track_id)

        self.spotify_obj.user_playlist_add_tracks(self.username, playlist_id, tracks_id)

    def createCopyPlaylist(self, username, playlist_name, public=False, description="new playlist"):
        # creates a new playlist
        self.spotify_obj.user_playlist_create(username, playlist_name, public=public, description=description)

    def getPlaylistID(self, playlist_name):
        # returns the id of a playlist given the name
        playlists = self.getUserPlaylists()
        return playlists[playlist_name]

    def getPlaylistOwnerID(self, playlist_id):
        # returns the id of the owner given the playlist id
        playlist_info = self.spotify_obj.playlist(playlist_id)
        return playlist_info["owner"]["id"]

    def followExistingPlaylist(self, playlist_id):
        # follows a playlist made by another owner given the id
        playlist_owner_id = self.getPlaylistOwnerID(playlist_id)
        self.spotify_obj.user_playlist_follow_playlist(playlist_owner_id, playlist_id)

    def topTracks(self):
        # returns all of the top tracks played by a user

        tracks = self.spotify_obj.current_user_top_tracks()

        return tracks

    def topArtists(self):
        # returns the top artists of a user

        artists = self.spotify_obj.current_user_top_artists()

        return artists