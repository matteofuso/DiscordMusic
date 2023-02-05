import re
import YOUTUBE

siteRegex = re.compile(r"^(?:https?://)?((([a-z]+)\.)?([A-Za-z0-9.-]+\.[A-Za-z]{2,}))")

# Get the type of promt
def promt(text, userid):
    isSite = re.search(siteRegex, text)
    # Gruppo 1: dominio completo
    # Gruppo 2: sottodominio + .
    # Gruppo 3: sottodominio
    # Gruppo 4: dominio
    # If the promt is a link
    if isSite:
        # If the site is Youtube
        fullDomain = isSite.group(1)
        if fullDomain in ("youtube.com", "www.youtube.com", "music.youtube.com"):
            # If the link is a video
            if "youtube.com/watch?" in text:
                # Search for the video id
                getVideo = text.split("youtube.com/watch?")[1].split("&")
                for parameter in getVideo:
                    if parameter.split("=")[0] == "v":
                        videoId = parameter.split("=")[1]
                        return {
                            "site": "Youtube",
                            "type": "video",
                            "id": videoId,
                            "url": f"https://{isSite.group(1)}/watch?v={videoId}"
                        }
            # If the link is a playlist
            elif "youtube.com/playlist?" in text:
                # Search for the playlist id
                getPlaylist = text.split("youtube.com/playlist?")[1].split("&")
                for parameter in getPlaylist:
                    if parameter.split("=")[0] == "list":
                        playlistId = parameter.split("=")[1]
                        return {
                            "site": "Youtube",
                            "type": "playlist",
                            "id": playlistId,
                            "url": f"https://{isSite.group(1)}/playlist?list={playlistId}"
                        }
            # If the link is not valid
            return {
                "error": "Il link di Youtube che hai inserito non è valido"
            }
        # If the site is Youtube Mobile
        elif fullDomain == "youtu.be":
            # If the link is a playlist
            if "youtu.be/playlist?" in text:
                # Search for the playlist id
                playlistId = text.split("youtu.be/playlist?")[1].split("&")
                for parameter in playlistId:
                    if parameter.split("=")[0] == "list":
                        playlistId = parameter.split("=")[1]
                        return {
                            "site": "Youtube",
                            "type": "playlist",
                            "id": playlistId,
                            "url": f"https://youtube.com/playlist?list={playlistId}"
                        }
            else:
                # If the link is a video
                videoId = text.split("youtu.be/")[1]
                if "&" in text:
                    # Search for the video id
                    videoId = videoId.split("&")[0]
                    return {
                        "site": "Youtube",
                        "type": "video",
                        "id": videoId,
                        "url": f"https://youtube.com/watch?v={videoId}"
                    }
            # If the link is not valid
            return {
                "error": "Il link di Youtube che hai inserito non è valido"
                }
        # If the site is Spotify - NOT SUPPORTED YET
        elif fullDomain in ("open.spotify.com", "play.spotify.com"):
            spotifyRegex = re.compile(r"^https?://(open|play)\.spotify\.com/(track|album|artist|playlist)/([a-zA-Z0-9]+)/?")
            isSpotify = spotifyRegex.match(text)
            # If the link is valid
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
        # If the site is SoundCloud - NOT SUPPORTED YET
        elif fullDomain == "soundcloud.com":
            return {
                "error": "SoundCloud non è ancora supportato"
            }
        # If the site is not supported
        else:
            return {
                "error": f"Il sito {fullDomain} non è supportato"
            }
    else:
        # If the text is a not a link search on Youtube
        return YOUTUBE.track_search(text, userid)