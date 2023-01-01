import json
import requests
from colorama import Fore, Style
import discord

try:
    with open("config.json", 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}
    print("Inserisci il token del bot:")

while True:
    if config.get("token") == None:
        config["token"] = input("> ")
    token = config["token"]
    head = {
        "Authorization": f"Bot {token}"
    }
    try:
        data = requests.get("https://discord.com/api/v10/users/@me", headers=head).json()
    except requests.exceptions.RequestException as e:
        if e.__class__ == requests.exceptions.ConnectionError:
            exit(f"{Fore.RED}ConnectionError{Fore.RESET}: Discord è bloccato nelle reti pubbliche, verifica di riuscire ad accedere a https://discord.com")

        elif e.__class__ == requests.exceptions.Timeout:
            exit(f"{Fore.RED}Timeout{Fore.RESET}: La connessione alle API di Discord ha impiegato troppo tempo (Sei rate limited?)")
        exit(f"Errore sconosciuto! Ulteriori informazioni:\n{e}")
    
    if data.get("id") != None:
        break
    print(f"{Fore.RED}Token non valido{Fore.RESET} Reinserisci il token: ")
    config.pop("token", None)

with open("config.json", "w") as f:
    f.write(json.dumps(config, indent=4))
    
class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(config["token"])