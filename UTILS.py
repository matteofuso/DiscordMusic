import re
import YOUTUBE


siteRegex = re.compile(r"^(?:https?://)?((([a-z]+)\.)?([A-Za-z0-9.-]+\.[A-Za-z]{2,}))")

def promt(text):
    isSite = re.search(siteRegex, text)
    # Gruppo 1: dominio completo
    # Gruppo 2: sottodominio + .
    # Gruppo 3: sottodominio
    # Gruppo 4: dominio
    if isSite:
        # If the site is Youtube
        fullDomain = isSite.group(1)
        if fullDomain == "youtube.com" or fullDomain == "www.youtube.com" or fullDomain == "music.youtube.com":
            # If the link is a Youtube Music link
            if isSite.group(3) == "music":
                isMusic = True
            else:
                isMusic = False
            # If the link is a video
            if "youtube.com/watch?" in text:
                getVideo = text.split("youtube.com/watch?")[1].split("&")
                for parameter in getVideo:
                    if parameter.split("=")[0] == "v":
                        videoId = parameter.split("=")[1]
                        return {
                            "site": "Youtube",
                            "isMusic": isMusic,
                            "type": "video",
                            "id": videoId,
                            "url": f"https://{isSite.group(1)}/watch?v={videoId}"
                        }
            # If the link is a playlist
            elif "youtube.com/playlist?" in text:
                getPlaylist = text.split("youtube.com/playlist?")[1].split("&")
                for parameter in getPlaylist:
                    if parameter.split("=")[0] == "list":
                        playlistId = parameter.split("=")[1]
                        return {
                            "site": "Youtube",
                            "isMusic": isMusic,
                            "type": "playlist",
                            "id": playlistId,
                            "url": f"https://{isSite.group(1)}/playlist?list={playlistId}"
                        }
            # If the link is not valid
            if videoId is None and playlistId is None:
                return {
                    "error": "Il link di Youtube che hai inserito non è valido"
                }
        
        # If the site is Youtube Mobile
        elif fullDomain == "youtu.be":
            if "youtu.be/playlist?" in text:
                playlistId = text.split("youtu.be/playlist?")[1].split("&")
                for parameter in playlistId:
                    if parameter.split("=")[0] == "list":
                        playlistId = parameter.split("=")[1]
                        return {
                            "site": "Youtube",
                            "isMusic": False,
                            "type": "playlist",
                            "id": playlistId,
                            "url": f"https://youtube.com/playlist?list={playlistId}"
                        }
            else:
                videoId = text.split("youtu.be/")[1]
                if "&" in text:
                    videoId = videoId.split("&")[0]
                    return {
                        "site": "Youtube",
                        "isMusic": False,
                        "type": "video",
                        "id": videoId,
                        "url": f"https://youtube.com/watch?v={videoId}"
                    }
                else:
                    return {
                        "error": "Il link di Youtube che hai inserito non è valido"
                    }
        
        # If the site is Spotify
        elif fullDomain == "open.spotify.com" or fullDomain == "play.spotify.com":
            spotifyRegex = re.compile(r"^https?://(open|play)\.spotify\.com/(track|album|artist|playlist)/([a-zA-Z0-9]+)/?")
            isSpotify = spotifyRegex.match(text)
            if isSpotify:
                return {
                    "site": "Spotify",
                    "type": isSpotify.group(2),
                    "id": isSpotify.group(3)
                }
            else:
                return {
                    "error": "Il link di Spotify che hai inserito non è valido"
                }
        elif fullDomain == "soundcloud.com":
            return {
                "error": "SoundCloud non è ancora supportato"
            }
        else:
            return {
                "error": f"Il sito {fullDomain} non è supportato"
            }
    else:
        # If the text is a not a link
        info = YOUTUBE.track_search(text)
        if len(info) == 0:
            return {
                "error": "Nessun risultato trovato"
            }
        return {
            "search": text,
            "data": info,
            "url": f"https://youtube.com/watch?v={info['id']}"
        }
        
print(promt("rick astley never gonna give you up"))