import yt_dlp
import json

debug = False

# Youtube-dl options
ydl_opts = {
    'format': 'm4a/bestaudio/best',
    'outtmpl': 'cache/music/YouTube_%(id)s.%(ext)s',
    "quiet": not debug
}

# Get video info
def videoInfo(func):
    try:
        # Get best quality cover
        cover = func["thumbnail"]
        for tumb in func["thumbnails"]:
            if not "resolution" in tumb:
                break
            cover = tumb["url"]
        # Debug data
        if debug:
            with open("debug.json", "w") as f:
                json.dump(func, f, indent=4)
        # Return data
        author = func["uploader"].replace(" - Topic", "")
        return {
            "id": func["id"],
            "name": func["title"],
            "cover": cover,
            "author": author,
            "duration": func["duration_string"]
        }
    except:
        return {
            "error": "Video not found"
        }

# Get video info
def track_fetch(url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        func = ydl.extract_info(url, download=False)
    return(videoInfo(func))

# Download video
def track_download(url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        func = ydl.extract_info(url, download=True)
        return f"./cache/music/YouTube_{func['id']}.{func['requested_downloads'][0]['ext']}"

# Search video
def track_search(query):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        func = ydl.extract_info(f"ytsearch:{query}", download=False)
    return(videoInfo(func["entries"][0]))