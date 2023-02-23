import requests
import json
import os

# Check for cache folder
if not os.path.exists("cache"):
    os.makedirs("cache")
if not os.path.exists("cache/cover"):
    os.makedirs("cache/cover")
if not os.path.exists("cache/music"):
    os.makedirs("cache/music")

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
        print("What's the token bot?")
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
            exit(f"ConnectionError: Discord is blocked in pubblic network, verify that you're able to connect to https://discord.com")
        elif e.__class__ == requests.exceptions.Timeout:
            exit(f"Timeout: Connection to Discord API take too long (Are you rate limited?)")
        exit(f"Unknown error! Other informations:\n{e}")
    # If the token is valid, break the loop
    if "id" in data:
        break
    # If the token is not valid, ask again
    print(f"Token is invalid. Reinsert it: ")
    config.pop("token", None)

# Save the token
if "volume" not in config:
    print("What's the bot default volume? (0-200) ")
    volume = int(input("> "))
    while volume <= 0 or volume > 200:
        print("Volume must be greater than 0 and less than 200. Reinsert the volume: ")
        volume = input("> ")
    config["volume"] = volume / 200
    
if "youtubeApiKey" not in config:
    print("Insert the YouTube l'API Key: ")
    youtubeApiKey = input("> ")
    config["youtubeApiKey"] = youtubeApiKey
    
def get_config():
    return config["token"], config["volume"]

with open("config.json", "w") as f:
    f.write(json.dumps(config, indent=4))