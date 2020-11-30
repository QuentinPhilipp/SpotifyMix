import requests
from flask import session
import json
import spotifyMix.spotifyCall as spotifyCall
from .models import db, User, Itinerary
import string
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
scopes = "user-library-read,playlist-modify-private,playlist-modify-public,playlist-read-private,playlist-read-collaborative"
from urllib.parse import urlencode

"""Logged-in page routes."""
from flask import Blueprint,flash,render_template, redirect, url_for,request,jsonify
from flask_login import current_user, login_required, logout_user
from .import login_manager

import os
from dotenv import load_dotenv
load_dotenv()
#
CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")

sp =None;


# Blueprint Configuration
main_bp = Blueprint(
    'main_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in upon page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('main_bp.login'))


@main_bp.route('/login')
def loginSpotify():
    global sp
    username=""
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    token = spotipy.util.prompt_for_user_token(username, scopes)
    if token:
        sp = spotipy.Spotify(auth=token)
        print("Token for user : ",token)
        session["token"] = token
        
        return redirect(url_for("main_bp.setNamePage"))
    else:
        print("Can't get token for", username)
        return jsonify("Token:",token)

@main_bp.route("/spotify/callback")
def spotify_callback():
    return "You can close this window!"

@main_bp.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@main_bp.route('/setname', methods=['GET'])
def setNamePage():
    return render_template("setname.html")

@main_bp.route('/setname', methods=['POST'])
def setName():
    sp = spotipy.Spotify(auth=session["token"])
    data = request.form
    if data is not None:
        playlistName = data['playlistName']
        if playlistName is not None:
            # Create a playlist with this name
            session["playlistName"] = playlistName
            print(f"Create new playlist :'{playlistName}'")
            sp.user_playlist_create(sp.current_user()["id"],playlistName,collaborative=True,public=False ,description="Playlist managed by Spotify Mix")
        else:
            #default name
            session["playlistName"] = "SpotifyMixPlaylist"
            sp.user_playlist_create(sp.current_user()["id"],"SpotifyMixPlaylist",collaborative=True,public=False ,description="Playlist managed by Spotify Mix")
    else:
        print("Error with data sent")

    return redirect(url_for("main_bp.share"))


@main_bp.route('/share', methods=['GET'])
def share():
    # Get the url for the shared playlist
    sp = spotipy.Spotify(auth=session["token"])
    userId = sp.current_user()['id']


    # Get all playlists from user
    playlists = sp.user_playlists(userId)
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            if playlist["name"]==session["playlistName"]:
                print("playlist : ",playlist)
                # session["playlistID"] = playlist['id']
                # session["playlistURI"] = playlist['uri']
                return render_template("share.html",playlistURI=playlist['uri'],playlistID=playlist['id'],playlistExternalURI=playlist["external_urls"]["spotify"])
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None

    print("Error playlist not created, redirect to home")
    return redirect(url_for("main_bp.home"))
