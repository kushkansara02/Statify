import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import matplotlib.pyplot as plt


class CredFlow(object):
    # class properties
    client_id = None
    client_secret = None
    spotify_obj = None

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.spotify_obj = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret))
        self.createSpotifyObj()

    def createSpotifyObj(self):
        # obtains authentication object from Spotify API
        self.spotify_obj = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret))

    def oneHitWonderChecker(self, artist, views_lim=0.5):
        query = self.spotify_obj.search("artist:" + artist, type="artist")
        items = query['artists']['items']
        if len(items) > 0:
            artist = items[0]
            followers = artist["followers"]["total"]
            id = artist["id"]
            genres = artist["genres"]
            popularity = artist["popularity"]

            response = self.spotify_obj.artist_top_tracks(id)
            top_tracks = []
            for track in response["tracks"]:
                top_tracks.append([track["name"], track["popularity"]])

            print(top_tracks)

            maximum = 0
            for i in range(len(top_tracks)):
                if top_tracks[i][1] > top_tracks[maximum][1]:
                    maximum = i

            maxSum = top_tracks[maximum][1]
            popSum = 0
            for track in top_tracks:
                popSum += track[1]

            if maxSum/popSum >= views_lim:
                return True
            else:
                return False

        else:
            raise Exception("Artist not found")

    def get_playlist_tracks(self, playlist_id):
        # gets all the tracks within a playlist { {"name":"id"}, ... }
        # extra steps necessary because request limit for the method is 100

        results = self.spotify_obj.playlist_items(playlist_id)
        tracks = results['items']
        track_info = {}

        while results['next']:
            results = self.spotify_obj.next(results)
            tracks.extend(results['items'])

        for x in range(results["total"]):
            track_info[tracks[x]["track"]["name"]] = tracks[x]["track"]["id"]

        return track_info

    def topFiftySplit(self):
        # can be sorted by explicit, artists, artist genre
        query = self.spotify_obj.search("Global Top 50", type="playlist")
        playlist_id = query["playlists"]["items"][0]["id"]
        tracks = self.get_playlist_tracks(playlist_id)

        all_artists = []
        freq = {}
        for track in tracks.keys():
            query = self.spotify_obj.search(track, type="track")
            artists = query["tracks"]["items"][0]["artists"]
            for i in range(len(artists)):
                all_artists.append(artists[i]["name"])
                freq[artists[i]["name"]] = 0

        for artist in all_artists:
            freq[artist] += 1

        labels = freq.keys()
        sizes = freq.values()

        patches, texts = plt.pie(sizes, shadow=True, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.axis('equal')
        plt.tight_layout()
        plt.show()