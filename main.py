import discord
from discord import app_commands, Intents, Client
import LIB.YOUTUBE as YOUTUBE
import LIB.SPOTIFY as SPOTIFY
import LIB.CONFIGS as CONFIGS
import LIB.UTILS as UTILS
import asyncio

# Get token and the default volume
token, defaultVolume = CONFIGS.get_config()

# Init bot
class Bot(Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    # Slash command tree
    async def setup_hook(self) -> None:
        await self.tree.sync()
client = Bot(intents=Intents.all())

# Manage guild
class Guild():
    # Init queue, volumes
    def __init__(self):
        self.queue = {}
        self.currentvolume = {}
        self.players = {}
    # Init the queue for a guild
    def init_queue(self, guild_id):
        if guild_id not in self.queue:
            self.queue[guild_id] = []
    # Add a song to the queue
    def add_queue(self, item, guild_id):
        # Check if the array is empty, then initialize it
        self.init_queue(guild_id)
        for song in item:
            self.queue[guild_id].append(song)
    # Get the a song from the queue
    def get_queue(self, guild_id, index=0):
        self.init_queue(guild_id)
        return self.queue[guild_id][index]
    # Remove a song from the queue
    def remove_queue(self, guild_id, index=0):
        self.init_queue(guild_id)
        self.queue[guild_id].pop(index)
    # How many songs are in the queue
    def size_queue(self, guild_id):
        self.init_queue(guild_id)
        return len(self.queue[guild_id])
    # Clear the queue
    def clear_queue(self, guild_id):
        self.init_queue(guild_id)
        self.queue[guild_id] = []
    def get_next(self, guild_id):
        self.remove_queue(guild_id)
        return self.get_queue(guild_id)
    # Set the volume
    def set_volume(self, guild_id, newvolume):
        self.currentvolume[guild_id] = newvolume
        if guild_id in self.players:
            self.players[guild_id].volume = newvolume
    # Get current volume
    def get_volume(self, guild_id):
        if guild_id not in self.currentvolume:
            return defaultVolume
        return self.currentvolume[guild_id]
guilds = Guild()
    
# Print bot info when ready
@client.event
async def on_ready():
    url = f"https://discord.com/api/oauth2/authorize?client_id={client.user.id}&scope=applications.commands"
    print(f"Loggato come {client.user} (ID: {client.user.id})\n\nUsa questo link per invitare {client.user} nel tuo server:\n{url}")
    # Set the bot presence - Uncomment the line you want to use
    #await client.change_presence(activity=discord.Game(name="")) # Playing ...
    #await client.change_presence(activity=discord.Streaming(name="", url="")) # Streaming ...
    #await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="")) # Listening to ...
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="my code")) # Watching ...

# Create an embed with the song info
def EmbedDetails(data, length, type="Riproducendo..."):
    if length == 0:
        return
    if data["toFetch"]:
        coverLink = data["cover"]
        if data["music"]:
            coverLink = YOUTUBE.cover(data["cover"], data["id"])
        duration, start = YOUTUBE.get_duration(data["id"])
    else:
        duration = data["duration"]
        start = data["start"]
        coverLink = data["cover"]
    if length == 1:
        description = f"[{data['title']} ({data['author']})]({data['url']}) [<@{data['user']}>]\nDurata: ` [{start} / {duration}] `"
    else:
        description = f"[{data['title']} ({data['author']})]({data['url']}) (E altri {length-1} elementi) [<@{data['user']}>]\nDurata: ` [{start} / {duration}] `"
    embed = discord.Embed(title=type, description=description)
    if data["coverLocal"]:
        file = discord.File(coverLink, filename="cover.jpg")  
        embed.set_thumbnail(url="attachment://cover.jpg")
    else:
        file = ""
        embed.set_thumbnail(url=coverLink)
    return embed, file

# Create an embed with the error
def EmbedError(error):
    embed = discord.Embed(title="Errore", description=error, color=0xFF0000)
    return embed

# Play command
@client.tree.command()
async def play(interaction: discord.Interaction, canzone: str):
    """Riproduci una canzone

    Parameters
    -----------
    canzone: str
        Nome o URL della canzone da riprodurre
    """
    # Defer the response
    await interaction.response.defer()
    # If the user is not connected to a voice channel
    if not interaction.user.voice:
        await interaction.followup.send(embed=EmbedError("Non sei connesso a un canale vocale."))
        return
    # If the bot is connected to a voice channel
    if interaction.guild.voice_client:
        # If the user is not connected to the same voice channel as the bot
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.followup.send(embed=EmbedError("You are not connected to the same voice channel as the bot."))
            return
    # Get datails about the promt
    format = UTILS.promt(canzone, interaction.user.id)
    search = False
    # If there is an error
    if "error" in format:
        await interaction.followup.send(embed=EmbedError(format["error"]))
        return
    # If the promt is not a link
    elif "site" in format:
        site = format["site"]
        data = []
    else:
        data = format["search"]
        site = "Youtube"
    # Check the site and fetch the song details
    if data != []:
        pass
    elif site == "Youtube":
        # If the promt is a link
        if not search:
            # Get the video details
            data = YOUTUBE.fetch(format["url"], interaction.user.id, format["type"], format["id"])
            # If there is an error
            if "error" in data:
                await interaction.followup.send(embed=EmbedError(data["error"]))
                return
    elif site == "Spotify":
        if format["type"] == "track":
            print(format["id"])
            data = SPOTIFY.track_metadata(format["id"], interaction.user.id)
            print(data)
        else:
            await interaction.followup.send(embed=EmbedError("Non puoi riprodurre una playlist o un album."))
            return
        if "error" in data:
            await interaction.followup.send(embed=EmbedError(data["error"]))
            return
    # If the bot is not connected to a voice channel
    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()
    voice_channel = interaction.guild.voice_client
    # Reply with the song info
    guild_id = str(interaction.guild.id)
    if voice_channel.is_paused() or voice_channel.is_playing():
        guilds.add_queue(data, guild_id)
        embed, file = EmbedDetails(data[0], len(data), "Aggiunto alla coda...")
        if file == "":
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(embed=embed, file=file)
        return
    else:
        embed, file = EmbedDetails(data[0], len(data))
        if file == "":
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(embed=embed, file=file)
    # Download the song
    if site == "Youtube":
        position = YOUTUBE.track_download(data[0]["id"])
    elif site == "Spotify":
        position = SPOTIFY.downlaod_track(data[0]["id"])
    # Play the song
    guilds.players[guild_id] = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(position))
    guilds.players[guild_id].volume = guilds.get_volume(guild_id)
    guilds.add_queue(data, guild_id)
    voice_channel.play(guilds.players[guild_id], after=lambda e: asyncio.run_coroutine_threadsafe(nextQueue(e, voice_channel, str(interaction.guild.id), interaction.channel), client.loop))

# Function that plays the next song in the queue
async def nextQueue(e, voice_channel, guild_id, text_channel):
    if e is not None:
        await text_channel.send(embed=EmbedError("Errore durante la riproduzione"))
        return
    size = guilds.size_queue(guild_id)
    if size == 0:
        return
    # Get the next song
    data = guilds.get_next(guild_id)
    # Reply with the song info
    embed, file = EmbedDetails(data, 1)
    if file == "":
        await text_channel.send(embed=embed)
    else:
        await text_channel.send(embed=embed, file=file)
    # Download the song
    if data["site"] == "Youtube":
        position = YOUTUBE.track_download(data["id"])
    elif data["site"] == "Spotify":
        position = SPOTIFY.downlaod_track(data["id"])
    # Play the song
    guilds.players[guild_id] = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(position))
    guilds.players[guild_id].volume = guilds.get_volume(guild_id)
    voice_channel.play(guilds.players[guild_id], after=lambda e: asyncio.run_coroutine_threadsafe(nextQueue(e, voice_channel, guild_id, text_channel), client.loop))

# Stop command
@client.tree.command()
async def skip(interaction: discord.Interaction):
    """Passa alla prossima canzone"""
    # Check if the user is connected to a voice channel
    if not interaction.user.voice:
        await interaction.response.send_message(embed=EmbedError("Non sei connesso a un canale vocale."))
        return
    # Check if the bot is connected to a voice channel
    if interaction.guild.voice_client:
        # Check if the user is connected to the same voice channel as the bot
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.response.send_message(embed=EmbedError("Non sei connesso al canale vocale del bot."))
            return
    else:
        # If the bot is not connected to a voice channel
        await interaction.response.send_message(embed=EmbedError("Il bot non è connesso a un canale vocale."))
        return
    # Check if the bot is playing a song
    voice_channel = interaction.guild.voice_client
    if not (voice_channel.is_playing() or voice_channel.is_paused()):
        await interaction.response.send_message(embed=EmbedError("Non stai riproducendo nulla."))
        return
    # Skip the song
    voice_channel.stop()
    await interaction.response.send_message("Riproduco la prossima canzone.")

# Volume control
@client.tree.command()
async def volume(interaction: discord.Interaction, volume: int):
    """Controlla il volume

    Parameters
    -----------
    volume: int
        Percentuale di volume da impostare
    """
    # Check if the bot is connected to a voice channel
    if interaction.guild.voice_client:
        # Check if the user is connected to the same voice channel as the bot
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.response.send_message(embed=EmbedError("Non sei connesso al canale vocale del bot."))
            return
    # Check if the volume is valid
    if volume <= 0 or volume > 200:
        await interaction.response.send_message(embed=EmbedError("Il volume deve essere compreso tra 0 e 200."))
        return
    guilds.set_volume(str(interaction.guild.id), volume / 200)
    await interaction.response.send_message(f"Volume impostato a {volume}%")

# Stop command
@client.tree.command()
async def stop(interaction: discord.Interaction):
    """Ferma la riproduzione"""
    # Check if the bot is connected to a voice channel
    if interaction.guild.voice_client:
        # Check if the user is connected to the same voice channel as the bot
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.response.send_message(embed=EmbedError("Non sei connesso al canale vocale del bot."))
            return
    else:
        # If the bot is not connected to a voice channel
        await interaction.response.send_message(embed=EmbedError("Il bot non è connesso a un canale vocale."))
        return
    # Clear the queue
    guilds.clear_queue(str(interaction.guild.id))
    # Check if the user is connected to a voice channel
    if not interaction.user.voice:
        await interaction.response.send_message(embed=EmbedError("Non sei connesso a un canale vocale."))
        return
    # Check if the bot is playing a song
    voice_channel = interaction.guild.voice_client
    if not (voice_channel.is_playing() or voice_channel.is_paused()):
        await interaction.response.send_message(embed=EmbedError("Non ci sono video da fermare."))
        return
    # Stop the song
    voice_channel.stop()
    await interaction.response.send_message("La riproduzione è stata fermata.")

# Pause command
@client.tree.command()
async def pause(interaction: discord.Interaction):
    """Pausa la canzone"""
    # Check if the user is connected to a voice channel
    if not interaction.user.voice:
        await interaction.response.send_message(embed=EmbedError("Non sei connesso a un canale vocale."))
        return
    # Check if the bot is connected to a voice channel
    if interaction.guild.voice_client:
        # Check if the user is connected to the same voice channel as the bot
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.response.send_message(embed=EmbedError("Non sei connesso al canale vocale del bot."))
            return
    else:
        # If the bot is not connected to a voice channel
        await interaction.response.send_message(embed=EmbedError("Il bot non è connesso a un canale vocale."))
        return
    # Check if the bot is playing a song
    voice_channel = interaction.guild.voice_client
    if not voice_channel.is_playing():
        await interaction.response.send_message(embed=EmbedError("Non sto riproducendo nulla."))
        return
    # Pause the song
    voice_channel.pause()
    await interaction.response.send_message("Ho messo in pausa la musica.")

# Resume command
@client.tree.command()
async def resume(interaction: discord.Interaction):
    """Riprende la canzone"""
    # Check if the user is connected to a voice channel
    if not interaction.user.voice:
        await interaction.response.send_message(embed=EmbedError("Non sei connesso a un canale vocale."))
        return
    # Check if the bot is connected to a voice channel
    if interaction.guild.voice_client:
        # Check if the user is connected to the same voice channel as the bot
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.response.send_message(embed=EmbedError("Non sei connesso al canale vocale del bot."))
            return
    else:
        # If the bot is not connected to a voice channel
        await interaction.response.send_message(embed=EmbedError("Il bot non è connesso a un canale vocale."))
        return
    # Check ther's a song paused
    voice_channel = interaction.guild.voice_client
    if not voice_channel.is_paused():
        await interaction.response.send_message(embed=EmbedError("Non ci sono canzoni in pausa."))
        return
    # Resume the song
    voice_channel.resume()
    await interaction.response.send_message("Ho ripreso la musica.")

# Run the bot
client.run(token)