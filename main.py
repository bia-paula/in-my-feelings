import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth

from flask import Flask, request, redirect, url_for, session

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
    result = []
    for track in top_tracks:
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

    emotions = []
    for track in features:
        energy = track['energy']
        valence = track['valence']
        emotions.append({'id': track['id'], 'emotion': [valence, energy]})

    return emotions




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