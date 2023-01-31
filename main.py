import discord
from discord import app_commands, Intents, Client
import YOUTUBE
import UTILS

# Get token
token = UTILS.get_token()

# Init bot
class Bot(Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.volume = 0.25

    async def setup_hook(self) -> None:
        await self.tree.sync()
    
    def set_volume(self, volume):
        self.volume = volume
        current_volume.volume = volume
        
client = Bot(intents=Intents.all())

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
def EmbedDetails(data, url, userID):
    description = f"[{data['name']} ({data['author']})]({url}) [<@{userID}>]\nDurata: ` [0:00 / {data['duration']}] `"
    embed = discord.Embed(title="Riproducendo", description=description)
    embed.set_thumbnail(url=data["cover"])
    return embed

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
    format = UTILS.promt(canzone)
    # If there is an error
    if "error" in format:
        await interaction.followup.send(embed=EmbedError(format["error"]))
        return
    # If the promt is not a link
    elif "search" in format:
        data = format["data"]
        site = "Youtube"
    else:
        site = format["site"]
        data = []
    # Check the site
    if site == "Youtube":
        # If the promt is a link
        if not "id" in data:
            # Get the video details
            data = YOUTUBE.track_fetch(format["url"])
            # If there is an error
            if "error" in data:
                await interaction.followup.send(embed=EmbedError(data["error"]))
                return
        # Reply with the song info
        await interaction.followup.send(embed=EmbedDetails(data, format["url"], interaction.user.id))
        # Download the song
        position = YOUTUBE.track_download(format["url"])
    else:
        # If the service is not supported yet
        await interaction.followup.send(embed=EmbedError("Supporto solo video di youtube per ora"))
        return
    # If the bot is not connected to a voice channel
    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()
    voice_channel = interaction.guild.voice_client
    # Play the song
    source = discord.FFmpegPCMAudio(position)
    player = discord.PCMVolumeTransformer(source)
    player.volume = client.volume
    voice_channel.play(player)
    global current_volume
    current_volume = player
    
# Volume control
@client.tree.command()
async def volume(interaction: discord.Interaction, volume: int):
    """Controlla il volume

    Parameters
    -----------
    volume: int
        Percentuale di volume da impostare
    """
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
    # Check if the volume is valid
    if volume <= 0 or volume > 200:
        await interaction.response.send_message(embed=EmbedError("Il volume deve essere compreso tra 0 e 200."))
        return
    client.set_volume(volume / 200)
    await interaction.response.send_message(f"Volume impostato a {volume}%")

# Stop command
@client.tree.command()
async def stop(interaction: discord.Interaction):
    """Ferma la riproduzione"""
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
    # Check if the bot is playing a song
    voice_channel = interaction.guild.voice_client
    if not voice_channel.is_playing():
        await interaction.response.send_message(embed=EmbedError("Non ci sono video da fermare."))
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
    # Check if the bot is playing a song
    voice_channel = interaction.guild.voice_client
    if not voice_channel.is_playing():
        await interaction.response.send_message(embed=EmbedError("Non sto riproducendo nulla."))
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
    # Check ther's a song paused
    voice_channel = interaction.guild.voice_client
    if not voice_channel.is_paused():
        await interaction.response.send_message(embed=EmbedError("Non ci sono canzoni in pausa."))
    # Resume the song
    voice_channel.resume()
    await interaction.response.send_message("Ho ripreso la musica.")

# Run the bot
client.run(token)