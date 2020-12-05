import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import matplotlib.pyplot as plt
import pickle


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
        items = query["artists"]["items"]
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
        tracks = results["items"]
        track_info = {}

        while results["next"]:
            results = self.spotify_obj.next(results)
            tracks.extend(results["items"])

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
        plt.axis("equal")
        plt.tight_layout()
        plt.show()

    def writeCategories(self):
        response = self.spotify_obj.categories(limit=50)
        categories = {}
        for item in response["categories"]["items"]:
            categories[item["name"]] = item["id"]
            print(categories[item["name"]] + " =  " + item["id"])

        with open("SpotifyData/categories.pickle", "wb") as file:
            pickle.dump(categories, file)

    def exploreCategory(self, category):
        with open("SpotifyData/categories.pickle", "rb") as file:
            categories = pickle.load(file)
            category_id = categories[category]

        category_info = self.spotify_obj.category(category_id=category_id)
        category_pic = category_info["icons"][0]["url"]

        category_playlists_response = self.spotify_obj.category_playlists(category_id=category_id, limit=50)
        category_playlists = {}

        for playlist in category_playlists_response["playlists"]["items"]:
            category_playlists[playlist["name"]] = playlist["id"]

        return [category_pic, category_playlists]

    def writeRecommendations(self):
        recommendations_response = self.spotify_obj.recommendation_genre_seeds()
        recommendations_list = []
        for genre in recommendations_response["genres"]:
            recommendations_list.append(genre)

        with open("SpotifyData/recommendation_seeds.pickle", "wb") as file:
            pickle.dump(recommendations_list, file)

    def generateRecommendations(self, seeds, seed_type="genre"):
        with open("SpotifyData/recommendation_seeds.pickle", "rb") as file:
            recommendations_list = pickle.load(file)

        if seed_type == "genre" and seed_type not in recommendations_list:
            raise ValueError("This genre is not accepted by the Spotify API")

        tracks = []
        if seed_type == "genre":
            tracks = self.spotify_obj.recommendations(seed_genres=seeds, limit=20)

        elif seed_type == "artist":
            id_seeds = []
            for seed in seeds:
                query = self.spotify_obj.search("artist:" + seed, type="artist")
                items = query["artists"]["items"]
                if len(items) > 0:
                    id_seeds.append(items[0]["id"])
            tracks = self.spotify_obj.recommendations(seed_artists=id_seeds, limit=20)

        else:
            id_seeds = []
            for seed in seeds:
                query = self.spotify_obj.search(seed, type="track")
                id_seeds.append(query["tracks"]["items"][0]["id"])
            tracks = self.spotify_obj.recommendations(seed_tracks=id_seeds, limit=20)

        recommended_tracks = []
        for track in tracks["tracks"]:
            artists = [artist["name"] for artist in track["artists"]]
            strArtists = ""
            for artist in artists:
                strArtists += str(artist) + " "

            track_info = {"artist": strArtists, "name": track["name"], "id": track["id"], "image": track["album"]["images"][0]}
            recommended_tracks.append(track_info)

        return recommended_tracks

    def audioFeatures(self, tracks):
        tracks_features = []
        for track in tracks:
            query = self.spotify_obj.search(track, type="track")
            track_id = query["tracks"]["items"][0]["id"]
            features = self.spotify_obj.audio_features([track_id])[0]
            features["name"] = track
            tracks_features.append(features)
        return tracks_features
