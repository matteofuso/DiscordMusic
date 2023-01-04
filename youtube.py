import json
import requests
import re 

try:
    with open("config.json", 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}

# Replace YOUR_API_KEY with your actual API key
api_key = config["youtube"]["key"]

def yt_video(link):
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

def yt_playlist(link):
    video_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={link}&key={api_key}"
    response = requests.get(video_url)
    video_data = response.json()
    videos = []
    try:
        data = video_data["items"]
        data[0]
        for video in data:
            videos.append({
            "name": video["snippet"]["title"],
            "author": video["snippet"]["videoOwnerChannelTitle"],
            "id": video["snippet"]["resourceId"]["videoId"]
            })
        return videos
    except IndexError:
        return False

def get_youtube(string):
    regex = r'^(https?://)?(www\.)?'
    regex += r'(youtube|youtu|youtube-nocookie)\.(com|be)/(.*)'
    match = re.search(regex, string)
    if match:
        link = (match.group(5))
        try:
            link = link.split("list=")[1].split("&")[0]
            return yt_playlist(link)
        except IndexError:
            if link.startswith("watch?"):
                link = link.split("&")[0]
                link = link.replace("watch?v=", "")
            else:
                link = link.split("?")[0]
        return yt_video(link)
    else:
        return False
    
print(json.dumps(get_youtube("https://www.youtube.com/watch?v=8Yg1FnKE66I&list=PLFSjo0XzsV12BG03Y2l7ojhVBjyPsg9HZ&index=3&t=16s"), indent=4))