import os, os.path
os.chdir("cache")
from librespot.core import Session
from librespot.metadata import TrackId
from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality
from getpass import getpass
import json
import requests
import datetime

TOKEN_REFRESH = 50 * 60 # A token is valid for 60 minutes, so we refresh it every 50 minutes

# Create a session
def login():
    global SESSION
    if os.path.isfile("credentials.json"):
        try:
            SESSION = Session.Builder().stored_file().create()
            return
        except:
            pass
    while True:
        user_name = input("Username Spotify: ")
        password = getpass("Password Spotify: ")
        try:
            SESSION = Session.Builder().user_pass(user_name, password).create()
            return
        except:
            pass
login()
os.chdir("..")


# Set the quality
if SESSION.get_user_attribute("type") == "premium":
    QUALITY = AudioQuality.VERY_HIGH
else:
    QUALITY = AudioQuality.HIGH

# Function to parse the duration
def format_duration(ms):
    total_seconds = int(ms / 1000)
    days = int(total_seconds // 86400)
    hours = int((total_seconds % 86400) // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    if days > 0:
        return f"{str(days).zfill(2)}:{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}", "00:00:00:00"
    if hours > 0:
        return f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}", "00:00:00"
    return f"{str(minutes).zfill(2)}:{str(seconds).zfill(2)}", "00:00"

# Function to get the token
def get_token():
    with open("config.json", "r") as configFile:
        config = json.load(configFile)
    if "spotify" in config:
        if "token" in config["spotify"]:
            token = config["spotify"]["token"]
            if int(datetime.datetime.now().timestamp()) > config["spotify"]["issued_at"] + TOKEN_REFRESH:
                token = SESSION.tokens().get("user-read-email")
                config["spotify"]["token"] = token
                config["spotify"]["issued_at"] = int(datetime.datetime.now().timestamp())
        else:
            config["spotify"]["token"] = token
            config["spotify"]["issued_at"] = int(datetime.datetime.now().timestamp())
    else:
        token = SESSION.tokens().get("user-read-email")
        config["spotify"] = {}
        config["spotify"]["token"] = token
        config["spotify"]["issued_at"] = int(datetime.datetime.now().timestamp())
    with open("config.json", "w") as configFile:
        json.dump(config, configFile, indent=4)
    return token

# Function to get the metadata
def track_metadata(id, userid):
    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json"
    }
    api = requests.get(f"https://api.spotify.com/v1/tracks/{id}", headers=headers)
    response = api.json()
    for artist in response["artists"]:
        artists = f"{artist['name']},"
    artists = artists[:-1]
    release_year = response["album"]["release_date"].split("-")[0]
    if QUALITY == AudioQuality.VERY_HIGH:
        bitrate = 320
    else:
        bitrate = 160
    id = response["id"]
    duration, start = format_duration(response["duration_ms"])
    return [
        {
        "id": id,
        "url": f"https://open.spotify.com/track/{id}",
        "album": response["album"]["name"],
        "cover": response["album"]["images"][0]["url"],
        "release-year": release_year,
        "artists": artists,
        "author": response["artists"][0]["name"],
        "title": response["name"],
        "track_number": response["track_number"],
        "bitrate": bitrate,
        "duration": duration,
        "toFetch": False,
        "start": start,
        "user": userid,
        "coverLocal": False,
        "site": "Spotify"
    }
    ]

# Download a track
def downlaod_track(id):
    track_id = TrackId.from_uri(f"spotify:track:{id}")
    stream = SESSION.content_feeder().load(track_id, VorbisOnlyAudioQuality(QUALITY), False, None)
    with open(f"./cache/music/Spotify_{id}.mp3", "wb") as file:
        while True:
            data = stream.input_stream.stream().read(1024)
            if len(data) == 0:
                break
            file.write(data)
    return f"./cache/music/Spotify_{id}.mp3"