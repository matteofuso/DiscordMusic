import json
import discord
from discord import app_commands, Intents, Client
import YOUTUBE
import UTILS

try:
    with open("config.json", 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    exit("config.json non trovato o non valido")
#    config = {}
#    print("Inserisci il token del bot:")

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


class Bot(Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        await self.tree.sync()


client = Bot(intents=Intents.all())


@client.event
async def on_ready():
    print(f"""Logged in as {client.user} (ID: {client.user.id})

Use this URL to invite {client.user} to your server:
https://discord.com/api/oauth2/authorize?client_id={client.user.id}&scope=applications.commands%20bot""")


def EmbedDetails(data, url, userID):
    description = f"[{data['name']} ({data['author']})]({url}) [<@{userID}>]\nDurata: ` [0:00 / {data['duration']}] `"
    embed = discord.Embed(title="Riproducendo", description=description)
    embed.set_thumbnail(url=data["cover"])
    return embed


def EmbedError(error):
    embed = discord.Embed(title="Errore", description=error, color=0xFF0000)
    return embed


@client.tree.command()
async def play(interaction: discord.Interaction, canzone: str):
    """Riproduci una canzone

    Parameters
    -----------
    canzone: str
        Nome o URL della canzone da riprodurre
    """
    await interaction.response.defer()
    if not interaction.user.voice:
        await interaction.followup.send(embed=EmbedError("Non sei connesso a un canale vocale."))
        return
    if interaction.guild.voice_client:
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.followup.send(embed=EmbedError("You are not connected to the same voice channel as the bot."))
            return
    format = UTILS.promt(canzone)
    if "error" in format:
        await interaction.followup.send(embed=EmbedError(format["error"]))
        return
    elif "search" in format:
        data = format["data"]
        site = "Youtube"
    else:
        site = format["site"]
        data = []
    if site == "Youtube":
        if not "id" in data:
            data = YOUTUBE.track_fetch(format["url"])
            if "error" in data:
                await interaction.followup.send(embed=EmbedError(data["error"]))
                return
        await interaction.followup.send(embed=EmbedDetails(data, format["url"], interaction.user.id))
        position = YOUTUBE.track_download(format["url"])
    else:
        await interaction.followup.send(embed=EmbedError("Supporto solo video di youtube per ora"))
        return

    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()
    voice_channel = interaction.guild.voice_client
    voice_channel.play(discord.FFmpegPCMAudio(position))


@client.tree.command()
async def stop(interaction: discord.Interaction):
    """Ferma la riproduzione"""
    if not interaction.user.voice:
        await interaction.response.send_message("Non sei connesso a un canale vocale.")
        return
    if interaction.guild.voice_client:
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.response.send_message("Non sei connesso al canale vocale del bot.")
            return
    else:
        if interaction.user.voice:
            await interaction.response.send_message("Non sei connesso a un canale vocale.")
            return
    voice_channel = interaction.guild.voice_client
    voice_channel.stop()
    await interaction.response.send_message("La riproduzione è stata fermata.")


@client.tree.command()
async def pause(interaction: discord.Interaction):
    """Pausa la canzone"""
    if not interaction.user.voice:
        await interaction.response.send_message("Non sei connesso a un canale vocale.")
        return
    if interaction.guild.voice_client:
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.response.send_message("Non sei connesso al canale vocale del bot.")
            return
    else:
        if interaction.user.voice:
            await interaction.response.send_message("Non sei connesso a un canale vocale.")
            return
    voice_channel = interaction.guild.voice_client
    voice_channel.pause()
    await interaction.response.send_message("Ho messo in pausa la musica.")


@client.tree.command()
async def resume(interaction: discord.Interaction):
    """Riprende la canzone"""
    if not interaction.user.voice:
        await interaction.response.send_message("Non sei connesso a un canale vocale.")
        return
    if interaction.guild.voice_client:
        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.response.send_message("Non sei connesso al canale vocale del bot.")
            return
    else:
        if interaction.user.voice:
            await interaction.response.send_message("Non sei connesso a un canale vocale.")
            return
    voice_channel = interaction.guild.voice_client
    voice_channel.resume()
    await interaction.response.send_message("Ho ripreso la musica.")

client.run(config["token"])