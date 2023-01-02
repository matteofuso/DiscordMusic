import json
import requests
from colorama import Fore, Style
import discord
from discord import app_commands, Interaction, Intents, Client
import re
from urllib.parse import urlparse



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

class FunnyBadge(Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        """ This is called when the bot boots, to setup the global commands """
        await self.tree.sync()
        
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
def is_youtube(string):
    regex = r'^(https?://)?(www\.)?'
    regex += r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
    regex += r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    match = re.search(regex, string)
    if match:
        return match.group(6)
    else:
        return False
    
def is_soundcloud(string):
    regex = r'^(https?://)?(www\.)?'
    regex += r'soundcloud\.com/[^/]+/[^/]+$'
    match = re.search(regex, string)
    if match:
        track = (string.split("/")[1]).split("?")[0]
        return track
    else:
        return False

@client.tree.command()
async def play(interaction: discord.Interaction, canzone: str):
    """Riproduci o aggiungi alla coda un pezzo :star:

    Parameters
    -----------
    canzone: str
        Nome o URL della canzone
    """
    if is_url(canzone):
        id = is_youtube(canzone)
        if id != False:
            embed = discord.Embed(title="Riproducendo", description=f"Codice Video yt: {id}", color=0x4f4f4f)
        else:
            id = is_soundcloud(canzone)
            if id !=False:
                embed = discord.Embed(title="Riproducendo", description=f"Codice Video soundcloud: {id}", color=0x4f4f4f)
            # else:
            #     if True:
            #         embed = discord.Embed(title="Riproducendo", description=f"Codice Video spotify: {id}", color=0x4f4f4f)
            else:
                embed = discord.Embed(title="Errore", description=f"Non è riprodurre musica da internet se non da youtube,soundcloud o spotify", color=0xf01e1e)
    else:
        embed = discord.Embed(title="Riproducendo", description=f"{canzone}", color=0x4f4f4f)
    await interaction.response.send_message(embed=embed)

client.run(config["token"])