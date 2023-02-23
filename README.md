# DiscordMusic

After Youtube has striked down all music bots, I decided to make my own bot for Discord. This bot is still working in progress. I will try to add more features as soon as possible.
Any suggestions are welcome (Please make pull requests / open an issue)! Here you can find the status of the project.

- [ ] Commands:
    - [x] Play
    - [x] Pause
    - [x] Resume
    - [x] Volume
    - [x] Queue
    - [x] Skip
    - [ ] Skip x songs
    - [ ] Shuffle
    - [ ] Config (Language, Credentials, etc.)

- [x] Type:
    - [x] Video
    - [x] Playlist

- [ ] Cache:
    - [ ] Auto delete file when the folder is bigger than xGB (configurable), in a FIFO way
    - [ ] Skip Fetching if the file is already in the cache

- [ ] Services:
    - [x] Youtube Music, Youtube
    - [ ] Spotify
    - [ ] Soundcloud
    - [ ] Deezer

- [ ] Features:
    - [x] Multi-Server
    - [ ] Trivia
    - [ ] Save queue in a file (When the bot is restarted, the queue is not lost)
    - [ ] Error handling
    - [ ] Music Download
    - [ ] Auto Update

# Install
Before you start, you need to install Python (Latest version is recommended), then install the requirements using:

    pip install -r requirements.txt

You can now start the bot using:

    python main.py

You'll need to insert:
- The bot token, you can get it from the [Discord Developer Portal](https://discord.com/developers/applications).
- The youtube api key, you can get it from the [Google Developer Console](https://console.developers.google.com/).
- Spotify credentials (They're needed to fetch song and metadata)

I suggest to not use your main account for YouTube and Spotify, because you can get banned if you use the bot too much.

# Update the bot
In order to update the bot is raccomanded to clone this repository locally with either https (Raccomended if you're using git for only this repository) or ssh. Before you have to install git, if you don't have it already. Then you can clone the repository using:

    git clone https://github.com/matteofuso/DiscordMusic.git
    git clone git@github.com:matteofuso/DiscordMusic.git

Then when you want to update the bot, you can use:

    git pull

I'll probably add a script to update the bot automatically.