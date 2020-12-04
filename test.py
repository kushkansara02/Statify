from SpotifyData import CredFlow, SpotipyClient

with open("SpotifyData/auth_data.txt", "r") as file:
    data = eval(file.read())
    client_id = data["client_id"]
    client_secret = data["client_secret"]

c = CredFlow(client_id, client_secret)
c.topFiftySplit()

#s = SpotipyClient("pgygx1h23ig1r8dbzu1ro9ma5", client_id, client_secret, "https://google.ca/")
#p = s.getUserPlaylists()
#print(p)