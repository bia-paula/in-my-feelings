import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth

from flask import Flask, request, redirect, url_for, session, render_template

import matplotlib.pyplot as plt
import numpy as np

import json

app = Flask(__name__)

app.config["SESSION_COOKIE_NAME"] = "Spotify Cookie"
app.secret_key = "fjifhjfiwqhbijvkblqeç+p%&"
TOKEN_INFO = "token_info"

@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('get_top_tracks', external=True))

@app.route('/getTopTracks')
def get_top_tracks():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect('/')

    sp = spotipy.Spotify(auth=token_info['access_token'])
    top_tracks = sp.current_user_top_tracks(time_range='short_term')['items']
    # top_tracks = sp.playlist_items("37i9dQZF1DX4o1oenSJRJd")['items']
    #print(top_tracks)
    result = []
    for element in top_tracks:
        #track = element['track'] # ------
        track = element
        artists = []
        for artist in track['artists']:
            artist = {'name': artist['name'],
                      'id': artist['id']}
            artists.append(artist)
        song = {'name': track['name'],
                  'id': track['id']}
        #result.append({'song': song, 'artist': artist})
        result.append(track['id'])

    return redirect(url_for('get_tracks_audio_features', values=','.join(result), external=True))

@app.route('/getTracksAudioFeatures')
def get_tracks_audio_features():
    ids = request.args['values']
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect('/')
    sp = spotipy.Spotify(auth=token_info['access_token'])
    features = sp.audio_features(ids.split(','))

    emotions = {}
    xs = []
    ys = []
    for track in features:
        energy = track['energy']
        valence = track['valence']
        emotions[track['id']] = {"emotion": [valence, energy]}
        xs.append(valence)
        ys.append(energy)

        song = sp.track(track['id'])
        emotions[song['id']]['name'] = song['name']
        artists = []
        for artist in song['artists']:
            artists.append(artist['name'])
        emotions[song['id']]['artists'] = artists

    labels = [f"{emotions[t_id]['name']} BY {', '.join(emotions[t_id]['artists'])}" for t_id in emotions.keys()]
    values = [{"x": emotions[t_id]["emotion"][0], "y": emotions[t_id]["emotion"][1]} for t_id in emotions.keys()]
    print(values)

    # plt.clf()
    # plt.scatter(xs, ys)
    #
    # for id in emotions.keys():
    #     x, y = emotions[id]["emotion"]
    #     label = emotions[id]["name"]
    #
    #     plt.annotate(label,  # this is the text
    #                  (x, y),  # these are the coordinates to position the label
    #                  textcoords="offset points",  # how to position the text
    #                  xytext=(0, 10),  # distance from text to points (x,y)
    #                  ha='center')  # horizontal alignment can be left, right or center

    out_file = open("emotions.json", "w")

    json.dump(emotions, out_file)

    out_file.close()

    #return emotions
    return render_template("graph.html", labels=labels, values=values)




def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login'), external=False)

    now = int(time.time())

    is_expired = token_info['expires_in'] - now < 60
    if is_expired:
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id='1a61cfdda502474ba91fa40badae76b6',
        client_secret='31de51e4bde04c5d83e59c08282f3053',
        redirect_uri=url_for('redirect_page', _external=True),
        scope='user-top-read',
    )

app.run(debug=True)