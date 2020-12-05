from SpotifyData import CredFlow, SpotipyClient
import pandas as pd
import matplotlib.pyplot as plt

## MAKE SURE TO CREATE A TEXT FILE WITH YOUR AUTH DATA
with open("SpotifyData/auth_data.txt", "r") as file:
    data = eval(file.read())
    client_id = data["client_id"]
    client_secret = data["client_secret"]

c = CredFlow(client_id, client_secret)
tracks = c.audioFeatures(["Keanu Reeves", "Headlines", "Maps", "I Mean It"])

df = pd.DataFrame(tracks)

analysis_metrics = ["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence"]
means = {}
for col in analysis_metrics:
    means[col] = df[col].mean()

labels = means.keys()
sizes = means.values()

patches, texts = plt.pie(sizes, shadow=True, startangle=90)
plt.legend(patches, labels, loc="best")
plt.axis("equal")
plt.tight_layout()
plt.show()

#s = SpotipyClient("pgygx1h23ig1r8dbzu1ro9ma5", client_id, client_secret, "https://google.ca/")
#p = s.getUserPlaylists()
#print(p)