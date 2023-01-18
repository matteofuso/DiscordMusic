import json
import discord
from discord import app_commands, Interaction, Intents, Client
from pytube import YouTube

try:
    with open("config.json", 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}
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

class musicBot(Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        """ This is called when the bot boots, to setup the global commands """
        await self.tree.sync()
        
client = musicBot(intents=Intents.all())

@client.event
async def on_ready():
     print(f"""Logged in as {client.user} (ID: {client.user.id})

Use this URL to invite {client.user} to your server:
https://discord.com/api/oauth2/authorize?client_id={client.user.id}&scope=applications.commands%20bot""")

@client.tree.command()
async def play(interaction: discord.Interaction, canzone: str):
    """Riproduci una canzone
    
    Parameters
    -----------
    canzone: str
        Nome o URL della canzone
    """
    if not interaction.user.voice:
        await interaction.response.send_message("You are not connected to a voice channel.")
        return
    if interaction.guild.voice_client:
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.response.send_message("You are not connected to the same voice channel as the bot.")
            return
    else:
        if interaction.user.voice:
            await interaction.user.voice.channel.connect()
    voice_channel = interaction.guild.voice_client
    # voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source="./cache/youtube_dQw4w9WgXcQ.mp3"))
    # await interaction.response.send_message("Riproduco riccardo")
    video = YouTube(f"{canzone}", on_progress_callback=progress_callback)
    await interaction.response.send_message(f'**Now playing:** {video.title}')
    audio_stream = video.streams.get_audio_only()
    print(f"Scaricando: {video.title} - {video.author}")
    audio_stream.download(f"./cache/", filename=f"1.mp3")
    
    voice_channel.play(discord.FFmpegPCMAudio("./cache/1.mp3"))  
  
@client.tree.command()
async def pause(interaction: discord.Interaction):
    """Pausa la canzone"""
    voice_channel = interaction.guild.voice_channel
    if voice_channel.is_playing():
        await voice_channel.pause()
    else:
        await interaction.response.send_message("The bot is not playing anything at the moment.")
    
@client.tree.command()
async def resume(interaction: discord.Interaction):
    """Riprendi la riproduzione della canzone"""
    voice_channel = interaction.guild.voice_channel
    if voice_channel.is_paused():
        await voice_channel.resume()
    else:
        await interaction.response.send_message("The bot was not playing anything before this. Use play_song command")

@client.tree.command()
async def stop(interaction: discord.Interaction):
    """Interrompe la canzone"""
    voice_channel = interaction.guild.voice_channel
    if voice_channel.is_playing():
        await voice_channel.stop()
    else:
        await interaction.response.send_message("The bot is not playing anything at the moment.")



def progress_callback(stream, chunk, bytes_remaining):
    # Calculate the progress as a percentage
    progress = (100 * (stream.filesize - bytes_remaining)) / stream.filesize
    # Print the progress bar
    progress = '█' * int(progress/4)
    print(f"\r↳ |{progress:<25}| {stream.filesize-bytes_remaining}/{stream.filesize} Bytes", end="")
    print("\n")

client.run(config["token"])