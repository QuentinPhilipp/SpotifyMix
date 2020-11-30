import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
load_dotenv()

def getPlaylists(sp):
    # os.environ["SPOTIPY_CLIENT_ID"] = clientID
    # os.environ["SPOTIPY_CLIENT_SECRET"] = clientSecret
    # os.environ["SPOTIPY_REDIRECT_URI"]="http://127.0.0.1:5000/spotifycallback"

    results = sp.current_user_saved_tracks()
    # print(results)
    print("Current user :",sp.current_user()["display_name"])
    me = sp.current_user()
    playlists = sp.user_playlists(me["id"])
    print("\nPlaylists :")
    nameList=[]
    for idx, item in enumerate(playlists['items']):
        name = item['name']
        nameList.append(name)
        print(idx, name, " – ", item['id'])

    if 'SpotifyMixPlaylist' not in nameList:
        sp.user_playlist_create(me["id"],"SpotifyMixPlaylist")
        print("\nPlaylist created")
    else:
        print("\nPlaylist already created")


def createSharedPlaylist(sp):
    print("Playlist not found, create the playlist")
    sp.user_playlist_create(sp.current_user()["id"],"SpotifyMixPlaylist",public=False ,description="Playlist managed by Spotify Mix")
    userId = sp.current_user()['id']
    # Get all playlists from user
    playlists = sp.user_playlists(userId)
    sharedPlaylistId = None
    for idx, item in enumerate(playlists['items']):
        if item["name"]=="SpotifyMixPlaylist":
            sharedPlaylistId = item['id']
    return sharedPlaylistId

def getIDSharedPlaylist(sp):
    # Get user id
    userId = sp.current_user()['id']
    # Get all playlists from user
    playlists = sp.user_playlists(userId)



    print("\nPlaylists :")
    nameList=[]
    for idx, item in enumerate(playlists['items']):
        name = item['name']
        nameList.append(name)
        print(idx, name, " – ", item['id'])

    sharedPlaylistId = None
    for idx, item in enumerate(playlists['items']):
        if item["name"]=="SpotifyMixPlaylist":
            sharedPlaylistId = item['id']
    else:
        sharedPlaylistId = createSharedPlaylist(sp)
    return sharedPlaylistId

if __name__ == '__main__':
    scope = "user-library-read, playlist-modify-private, playlist-modify-public, playlist-read-private"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    # getPlaylists(sp)
    playlistID = getIDSharedPlaylist(sp)
    print(playlistID)
