import json
import requests
from colorama import Fore, Style
import discord
from discord import app_commands, Interaction, Intents, Client
from discord.ext import commands,tasks
import re
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
import youtube_dl
import asyncio

load_dotenv()

try:
    with open("config.json", 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}
    print("Inserisci il token del bot:")
    
try:
    config["token"]
except KeyError:
    print("Inserisci il token del bot:")

# while True:
#     if config.get("token") == None:
#         config["token"] = input("> ")
#     token = config["token"]
#     head = {
#         "Authorization": f"Bot {token}"
#     }
#     try:
#         data = requests.get("https://discord.com/api/v10/users/@me", headers=head).json()
#     except requests.exceptions.RequestException as e:
#         if e.__class__ == requests.exceptions.ConnectionError:
#             exit(f"{Fore.RED}ConnectionError{Fore.RESET}: Discord è bloccato nelle reti pubbliche, verifica di riuscire ad accedere a https://discord.com")

#         elif e.__class__ == requests.exceptions.Timeout:
#             exit(f"{Fore.RED}Timeout{Fore.RESET}: La connessione alle API di Discord ha impiegato troppo tempo (Sei rate limited?)")
#         exit(f"Errore sconosciuto! Ulteriori informazioni:\n{e}")
    
#     if data.get("id") != None:
#         break
#     print(f"{Fore.RED}Token non valido{Fore.RESET} Reinserisci il token: ")
#     config.pop("token", None)

# with open("config.json", "w") as f:
#     f.write(json.dumps(config, indent=4))

# Bot Start

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class FunnyBadge(Client, discord.PCMVolumeTransformer):
    def __init__(self, source, *,data, intents: Intents, stream=False):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        """ This is called when the bot boots, to setup the global commands """
        await self.tree.sync()
        
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename
        
client = FunnyBadge(intents=Intents.none())

@client.event
async def on_ready():
#     print(f"""
# Logged in as {client.user} (ID: {client.user.id})

# Use this URL to invite {client.user} to your server:
# {Fore.LIGHTBLUE_EX}https://discord.com/api/oauth2/authorize?client_id={client.user.id}&scope=applications.commands%20bot{Fore.RESET}
# """)
    print("Logged")

def is_url(string):
   try:
       result = urlparse(string)
       return all([result.scheme, result.netloc])
   except ValueError:
       return False
   
def get_youtube(string):
    regex = r'^(https?://)?(www\.)?'
    regex += r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
    regex += r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    match = re.search(regex, string)
    if match:
        return (match.group(6)).split("?")[0]
    else:
        return False
    
def get_soundcloud(string):
    regex = r'^(https?://)?(www\.)?'
    regex += r'soundcloud\.com/[^/]+/[^/]+$'
    match = re.search(regex, string)
    if match:
        track = string.split("/")
        track = track[1] + track[2]
        track = track.split("?")[0]
        return track
    else:
        return False
    
def get_spotify(string):
    track_regex = r'^(https?://)?(open|play|www)\.spotify\.com/track/([^/]+)$'
    playlist_regex = r'^(https?://)?(open|play|www)\.spotify\.com/user/([^/]+)/playlist/([^/]+)$'
    track_match = re.search(track_regex, string)
    if track_match:
        track_id = track_match.group(3)
        return {"type": "track", "id": track_id}
    else:
        playlist_match = re.search(playlist_regex, string)
        if playlist_match:
            playlist_id = (playlist_match.group(4)).split("?")[0]
            return {"type": "playlist", "id": playlist_id}
        else:
            return False

@client.tree.command()
async def play(interaction: discord.Interaction, canzone: str):
    """Riproduci o aggiungi alla coda un pezzo

    Parameters
    -----------
    canzone: str
        Nome o URL della canzone
    """
    if is_url(canzone):
        id = get_youtube(canzone)
        if id != False:
            embed = discord.Embed(title="Riproducendo", description=f"Codice Video yt: {id}", color=0x4f4f4f)
        else:
            id = get_soundcloud(canzone)
            if id !=False:
                embed = discord.Embed(title="Riproducendo", description=f"Codice Video soundcloud: {id}", color=0x4f4f4f)
            else:
                id = get_spotify(canzone)
                if id != False:
                    embed = discord.Embed(title="Riproducendo", description=f"Codice Video spotify: {id['id']}", color=0x4f4f4f)
                else:
                    embed = discord.Embed(title="Errore", description=f"Non è riprodurre musica da internet se non da youtube,soundcloud o spotify", color=0xf01e1e)
    else:
        embed = discord.Embed(title="Riproducendo", description=f"{canzone}", color=0x4f4f4f)
    await interaction.response.send_message(embed=embed)


@client.tree.command()
async def join(interaction: discord.Interaction, ctx):
    """Tells the bot to join the voice channel"""
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()
    
@client.tree.command()
async def leave(interaction: discord.Interaction, ctx):
    """To make the bot leave the voice channel"""
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

client.run(config["token"])