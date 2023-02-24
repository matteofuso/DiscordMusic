"""
YouTube Downloader
~~~~~~~~~~~~~~~~~~~~~

This module allows you to download tracks from YouTube.

Functions:

    convert_duration(duration) -> return the formatted duration of a track
    
    cover_url(url, id) -> crop an image and return the path to the file
    
    get_duration(id) -> return the duration of a track
    
    parsed(video, userid, music, moreInfo) -> format the youtube json response
    
    fetch(url, userid, type, id) -> return the metadata of a track
    
    track_download(id) -> download a track and return the path to the file
    
    track_search(query, userid) -> search a track and return the metadata of the first result
"""

import yt_dlp
import requests
from PIL import Image
import os
import re
import json

debug = False

# Youtube-dl options
ydl_opts = {
    'format': 'm4a/bestaudio/best',
    'outtmpl': './cache/music/YouTube_%(id)s.%(ext)s',
    "quiet": not debug
}

# Get the Youtube API key
with open("config.json", "r") as configFile:
    api_key = json.load(configFile)["youtubeApiKey"]

# Function to convert youtube duration to a readable format
def convert_duration(duration):
    match = re.search(r'P(?P<days>\d+D)?T(?P<hours>\d+H)?(?P<minutes>\d+M)?(?P<seconds>\d+S)?', duration)
    if not match:
        return ""
    days = match.group('days')[:-1] if match.group('days') else "0"
    hours = match.group('hours')[:-1] if match.group('hours') else "0"
    minutes = match.group('minutes')[:-1] if match.group('minutes') else "0"
    seconds = match.group('seconds')[:-1] if match.group('seconds') else "0"
    if days != "0":
        return f"{days.zfill(2)}:{hours.zfill(2)}:{minutes.zfill(2)}:{seconds.zfill(2)}", "00:00:00:00"
    elif hours != "0":
        return f"{hours.zfill(2)}:{minutes.zfill(2)}:{seconds.zfill(2)}", "00:00:00"
    elif minutes != "0":
        return f"{minutes.zfill(2)}:{seconds.zfill(2)}", "00:00"
    else:
        return f"00:{seconds.zfill(2)}", "00:00"

# Function to downlad and crop the cover as a square
def cover(url, id):
    image = requests.get(url)
    with open(f"./cache/cover/YouTube_{id}.jpg", "wb") as f:
        f.write(image.content)
    img = Image.open(os.path.join(os.getcwd(), f"./cache/cover/YouTube_{id}.jpg"))
    w = img.size[0]
    h = img.size[1]
    crop = int((w - h)/2)
    box = (crop, 0, w - crop, h)
    cropped_img = img.crop(box)
    cropped_img.save(os.path.join(os.getcwd(), f"./cache/cover/YouTube_{id}.jpg"))
    return f"cache/cover/YouTube_{id}.jpg"

# Function to fetch the duration of a video
def get_duration(id):
    video_endpoint = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={id}&key={api_key}"
    video_response = requests.get(video_endpoint)
    video_data = video_response.json()
    return convert_duration(video_data["items"][0]["contentDetails"]["duration"])

# Function to parse the video information
def parsed(video, userid, music, moreInfo):
    # Get the video ID, title, author and cover
    if video["kind"] == "youtube#video":
        id = video["id"]
        title = video["snippet"]["title"]
        author = video["snippet"]["channelTitle"]
        duration, start = convert_duration(video["contentDetails"]["duration"])
    elif video["kind"] == "youtube#playlistItem":
        id = video["snippet"]["resourceId"]["videoId"]
        title = video["snippet"]["title"]
        author = video["snippet"]["videoOwnerChannelTitle"]
        duration = ""
        start = ""
    else:
        id = video["id"]["videoId"]
        title = video["snippet"]["title"]
        author = video["snippet"]["channelTitle"]
        duration = ""
        start = ""
    # Downlaod the cover
    coverLink = f"https://i.ytimg.com/vi/{id}/maxresdefault.jpg"
    # Crop the cover if it's a music video
    link = f"https://www.youtube.com/watch?v={id}"
    if music:
        link = f"https://music.youtube.com/watch?v={id}"
        if moreInfo:
            coverLink = cover(coverLink, id)
    if moreInfo and duration == "":
        duration, start = get_duration(id)
    # Remove the "- Topic" from the author name
    if author.endswith(" - Topic"):
        author = author[:-8]
    # Return the video information
    return {
        "id": id,
        "url": link,
        "title": title,
        "author": author,
        "cover": coverLink,
        "music": music,
        "toFetch": not moreInfo,
        "coverLocal": music,
        "duration": duration,
        "user": userid,
        "site": "Youtube",
        "start": start
    }

# Function to fetch the video information
def fetch(url, userid, type, id):    
    videos = []
    page = ""
    firstDownloaded = False
    # Check if the link is a music video
    if "music.youtube.com" in url:
        music = True
    else:
        music = False
    while True:
        if type == "video":
            fetch = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={id}&key={api_key}"
        else:
            fetch = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails&playlistId={id}&key={api_key}&maxResults=50{page}"
        response = requests.get(fetch)
        jsonResp = response.json()
        for item in jsonResp["items"]:
            videos.append(parsed(item, userid, music, not firstDownloaded))
            if not firstDownloaded:
                firstDownloaded = True
        if not "nextPageToken" in jsonResp:
            break
        token = jsonResp["nextPageToken"]
        page = f"&pageToken={token}"
    return videos

# Download video
def track_download(id):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        func = ydl.extract_info(f"https://www.youtube.com/watch?v={id}", download=True)
        return f"./cache/music/YouTube_{id}.{func['requested_downloads'][0]['ext']}"

# Search video
def track_search(query, userid):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={query}&type=video&key={api_key}"
    response = requests.get(url)
    data = response.json()
    parse = parsed(data["items"][0], userid, False, True)
    return {
        "search": [
            parse
        ]
    }