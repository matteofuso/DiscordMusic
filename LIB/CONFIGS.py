import requests
import json
import os

# Get the config file
try:
    with open("config.json", 'r') as f:
        config = json.load(f)
# If the file doesn't exist or it's not valid
except (FileNotFoundError, json.JSONDecodeError):
    config = {}

while True:
    # If the token is not in the config file
    if "token" not in config:
        print("Inserisci il token del bot:")
        config["token"] = input("> ")
    # Check if the token is valid
    token = config["token"]
    head = {
        "Authorization": f"Bot {token}"
    }
    try:
        data = requests.get(
            "https://discord.com/api/v10/users/@me", headers=head).json()
    except requests.exceptions.RequestException as e:
        if e.__class__ == requests.exceptions.ConnectionError:
            exit(f"ConnectionError: Discord è bloccato nelle reti pubbliche, verifica di riuscire ad accedere a https://discord.com")
        elif e.__class__ == requests.exceptions.Timeout:
            exit(f"Timeout: La connessione alle API di Discord ha impiegato troppo tempo (Sei rate limited?)")
        exit(f"Errore sconosciuto! Ulteriori informazioni:\n{e}")
    # If the token is valid, break the loop
    if "id" in data:
        break
    # If the token is not valid, ask again
    print(f"Token non valido Reinserisci il token: ")
    config.pop("token", None)

# Save the token
if "volume" not in config:
    print("Inserisci il volume default (0-200): ")
    volume = int(input("> "))
    while volume <= 0 or volume > 200:
        print("Il volume deve essere compreso tra 0 e 200. Reinserisci il volume: ")
        volume = input("> ")
    config["volume"] = volume / 200
    
if "youtubeApiKey" not in config:
    print("Inserisci l'API Key di Youtube: ")
    youtubeApiKey = input("> ")
    config["youtubeApiKey"] = youtubeApiKey
    
def get_config():
    return config["token"], config["volume"]

with open("config.json", "w") as f:
    f.write(json.dumps(config, indent=4))