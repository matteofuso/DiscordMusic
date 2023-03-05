# Discord bot that lets you listening to youtube videos on discord with your friends through a link
import discord
from discord import app_commands, Intents, Client
from LIB import CONFIGS, YOUTUBE, SPOTIFY, UTILS
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
    print(f"Logged as {client.user} (ID: {client.user.id})\n\n Use this link to invite {client.user} in your server:\n{url}")
    # Set the bot presence - Uncomment the line you want to use
    #await client.change_presence(activity=discord.Game(name="")) # Playing ...
    #await client.change_presence(activity=discord.Streaming(name="", url="")) # Streaming ...
    #await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="")) # Listening to ...
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="my code")) # Watching ...

# Create an embed with the song info
def EmbedDetails(data, length, type="Playing..."):
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
        description = f"[{data['title']} ({data['author']})]({data['url']}) [<@{data['user']}>]\nDuration: ` [{start} / {duration}] `"
    else:
        description = f"[{data['title']} ({data['author']})]({data['url']}) (Others {length-1} elements) [<@{data['user']}>]\nDuration: ` [{start} / {duration}] `"
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
    embed = discord.Embed(title="Error", description=error, color=0xFF0000)
    return embed

# Play command
@client.tree.command()
async def play(interaction: discord.Interaction, song: str):
    """Play a song

    Parameters
    -----------
    song: str
        Name or URL of the song to play (Supported YouTube, Spotify)
    """
    # Defer the response
    await interaction.response.defer()
    # If the user is not connected to a voice channel
    if not interaction.user.voice:
        await interaction.followup.send(embed=EmbedError("You are not in a voice channel."))
        return
    # If the bot is connected to a voice channel
    if interaction.guild.voice_client:
        # If the user is not connected to the same voice channel as the bot
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.followup.send(embed=EmbedError("You are not connected to the same voice channel as the bot."))
            return
    # Get datails about the promt
    format = UTILS.promt(song)
    search = False
    # If there is an error
    if "error" in format:
        await interaction.followup.send(embed=EmbedError(format["error"]))
        return
    # If the promt is not a link
    elif "site" in format:
        site = format["site"]
    else:
        data = format["search"]
        site = "Youtube"
    # Check the site and fetch the song details
    if site == "toSearch":
        site = "Youtube"
        data = YOUTUBE.track_search(song, interaction.user.id)["search"]
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
            data = SPOTIFY.track_metadata(format["id"], interaction.user.id)
        else:
            await interaction.followup.send(embed=EmbedError("You can not play a playlist or an album at the moment."))
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
        embed, file = EmbedDetails(data[0], len(data), "Added to the queue...")
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
        await text_channel.send(embed=EmbedError("Error during riproduction of the song"))
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
    """Skip to the next song"""
    # Check if the user is connected to a voice channel
    if not interaction.user.voice:
        await interaction.response.send_message(embed=EmbedError("You are not in a voice channel."))
        return
    # Check if the bot is connected to a voice channel
    if interaction.guild.voice_client:
        # Check if the user is connected to the same voice channel as the bot
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.response.send_message(embed=EmbedError("You are not in the same voice channel of the bot."))
            return
    else:
        # If the bot is not connected to a voice channel
        await interaction.response.send_message(embed=EmbedError("Bot is not in a voice channel."))
        return
    # Check if the bot is playing a song
    voice_channel = interaction.guild.voice_client
    if not (voice_channel.is_playing() or voice_channel.is_paused()):
        await interaction.response.send_message(embed=EmbedError("You are playing nothing."))
        return
    # Skip the song
    voice_channel.stop()
    await interaction.response.send_message("Playing the next song.")

# Volume control
@client.tree.command()
async def volume(interaction: discord.Interaction, volume: int):
    """Check the volume

    Parameters
    -----------
    volume: int
        Percentage of volume
    """
    # Check if the bot is connected to a voice channel
    if interaction.guild.voice_client:
        # Check if the user is connected to the same voice channel as the bot
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.response.send_message(embed=EmbedError("You are not in the bot voice channel."))
            return
    # Check if the volume is valid
    if volume <= 0 or volume > 200:
        await interaction.response.send_message(embed=EmbedError("Volume must be greater than 0 and less than 200."))
        return
    guilds.set_volume(str(interaction.guild.id), volume / 200)
    await interaction.response.send_message(f"Volume set to {volume}%")

# Stop command
@client.tree.command()
async def stop(interaction: discord.Interaction):
    """Stop reproduction"""
    # Check if the bot is connected to a voice channel
    if interaction.guild.voice_client:
        # Check if the user is connected to the same voice channel as the bot
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.response.send_message(embed=EmbedError("You are not in the bot voice channel."))
            return
    else:
        # If the bot is not connected to a voice channel
        await interaction.response.send_message(embed=EmbedError("Bot is not in a voice channel."))
        return
    # Clear the queue
    guilds.clear_queue(str(interaction.guild.id))
    # Check if the user is connected to a voice channel
    if not interaction.user.voice:
        await interaction.response.send_message(embed=EmbedError("You are not in a voice channel."))
        return
    # Check if the bot is playing a song
    voice_channel = interaction.guild.voice_client
    if not (voice_channel.is_playing() or voice_channel.is_paused()):
        await interaction.response.send_message(embed=EmbedError("There aren't any song to stop."))
        return
    # Stop the song
    voice_channel.stop()
    await interaction.response.send_message("Reproduction has been stopped.")

# Pause command
@client.tree.command()
async def pause(interaction: discord.Interaction):
    """Stop the song"""
    # Check if the user is connected to a voice channel
    if not interaction.user.voice:
        await interaction.response.send_message(embed=EmbedError("You are not in a voice channel."))
        return
    # Check if the bot is connected to a voice channel
    if interaction.guild.voice_client:
        # Check if the user is connected to the same voice channel as the bot
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.response.send_message(embed=EmbedError("You are not in the bot voice channel."))
            return
    else:
        # If the bot is not connected to a voice channel
        await interaction.response.send_message(embed=EmbedError("Bot is not in a voice channel."))
        return
    # Check if the bot is playing a song
    voice_channel = interaction.guild.voice_client
    if not voice_channel.is_playing():
        await interaction.response.send_message(embed=EmbedError("I ain't playing anything."))
        return
    # Pause the song
    voice_channel.pause()
    await interaction.response.send_message("I paused the song.")

# Resume command
@client.tree.command()
async def resume(interaction: discord.Interaction):
    """Resume the song"""
    # Check if the user is connected to a voice channel
    if not interaction.user.voice:
        await interaction.response.send_message(embed=EmbedError("You are not in a voice channel."))
        return
    # Check if the bot is connected to a voice channel
    if interaction.guild.voice_client:
        # Check if the user is connected to the same voice channel as the bot
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.response.send_message(embed=EmbedError("You are not in the bot voice channel."))
            return
    else:
        # If the bot is not connected to a voice channel
        await interaction.response.send_message(embed=EmbedError("Bot is not in a voice channel."))
        return
    # Check ther's a song paused
    voice_channel = interaction.guild.voice_client
    if not voice_channel.is_paused():
        await interaction.response.send_message(embed=EmbedError("There are no paused songs"))
        return
    # Resume the song
    voice_channel.resume()
    await interaction.response.send_message("I've just resumed the current queue.")

# Run the bot
client.run(token)