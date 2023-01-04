import json
import requests
import re
from pytube import YouTube

try:
    with open("config.json", 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}
api_key = config["youtube"]["key"]

def video(link):
    video_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={link}&key={api_key}"
    response = requests.get(video_url)
    video_data = response.json()
    try:
        data = video_data["items"][0]
        return {
            "name": data["snippet"]["title"],
            "author": data["snippet"]["channelTitle"],
            "id": data["id"]
        }
    except IndexError:
        return False

def playlist(link):
    next = ""
    remaining = ""
    videos = []
    while True:
        video_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={link}&key={api_key}&maxResults=50{next}"
        response = requests.get(video_url)
        video_data = response.json()
        try:
            data = video_data["items"]
            data[0]
            for video in data:
                videos.append({
                "name": video["snippet"]["title"],
                "author": video["snippet"]["videoOwnerChannelTitle"],
                "id": video["snippet"]["resourceId"]["videoId"]
                })
            try:
                pageToken = video_data["nextPageToken"]
                next = f"&pageToken={pageToken}"
                if remaining == "":
                    remaining = video_data["pageInfo"]["totalResults"] - 50
                else:
                    remaining = remaining - 50
            except KeyError:
                remaining = 0
        except IndexError:
            return False
        if remaining < 0:
            break
    return videos

def get(string):
    regex = r'^(https?://)?(www\.)?'
    regex += r'(music.youtube|youtube|youtu|youtube-nocookie)\.(com|be)/(.*)'
    match = re.search(regex, string)
    if match:
        link = (match.group(5))
        try:
            link = link.split("list=")[1].split("&")[0]
            return playlist(link)
        except IndexError:
            if link.startswith("watch?"):
                link = link.split("&")[0]
                link = link.replace("watch?v=", "")
            else:
                link = link.split("?")[0]
        return video(link)
    else:
        return False
    
def download_id(id):
    video = YouTube(f"https://www.youtube.com/watch?v={id}")
    video.streams.get_audio_only().download(f"./cache/", filename=f"youtube_{id}.mp3")
        
def download_link(link):
    ids = get(link)
    if ids != False:
        try:
            ids[1]
        except KeyError:
            download_id(ids["id"])
    
download_link("https://music.youtube.com/watch?v=4ywb2pXRYZI&feature=share")