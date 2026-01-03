# PSN Bot

A custom Discord bot for retrieving PlayStation Network (PSN) details like profiles, trophies, recent games, game searches, and more. Built from the ground up by **evangelions**!

## Features

- **User Profiles** – Full PSN account info (trophies, friends, region, about me, presence, etc.)
- **Trophy Summary** – Bronze/Silver/Gold/Platinum counts and level progress
- **Game Search** – Detailed game info via IGDB (description, genres, artwork, videos)
- **Recent Games** – List of recently played titles
- **Avatar Tools** – Verify, add to cart, or remove PSN avatars (ephemeral commands)
- **Bot Info** – Ping, server list, credits
- **Owner Tools** – Ban/unban users, refresh PSN token
- **Customizable** – Status rotation, channel restrictions, invite links

---

## Prerequisites

Before starting, make sure you have:

- **Python 3.10 or higher** installed ([download here](https://www.python.org/downloads/))
- **Git** installed ([download here](https://git-scm.com/downloads))
- A **Discord account**
- A **PlayStation Network account**
- A **Twitch Developer account** (free)

---

## Setup Guide (Step-by-Step)

### 1. Clone the Repository

Open a terminal/command prompt and run:

```
git clone https://github.com/evangelions/v-PSN-bot.git
cd v-PSN-bot
```
This creates a folder called v-PSN-bot with all the files.

### 2. Install Required Packages

In the same terminal (inside the v-PSN-bot folder), run:

```
pip install -r requirements.txt
```
If you get errors about discord.py, fix it with:
```
pip uninstall discord.py
pip install discord.py==2.3.2
```

### 3. Get Your API Keys & Tokens

**Discord Bot Token**

1. Go to Discord Developer Portal
2. Click New Application → give it a name → Create
3. Go to Bot section → Add Bot → Yes, do it!
4. Under Token, click Copy (keep this secret!)
5. Go to OAuth2 → URL GeneratorScopes: bot
6. Bot Permissions: Send Messages, Embed Links, Read Message History, Use Slash Commands
7. Copy the generated link and open it to invite the bot to your server

**PSN NPSSO Cookie**

1. Open Chrome/Firefox and log in to playstation.com
2. In the same browser tab (don't close or log out), open a new tab and paste this exact URL: https://ca.account.sony.com/api/v1/ssocookie
3. Refresh the page
4. you'll see a page with JSON text like this:
   {"npsso":"a_long_64_character_code_here"}
6. Copy the long code inside the quotes after "npsso": (it's 64 characters).
7. This is your NPSSO – it expires after a while, so you may need to refresh it later

**IGDB (Twitch) Keys**

1. Go to Twitch Developer Console
2. Click Register Your Application
3. Name: anything (e.g., "PSN Bot")
4. OAuth Redirect URL: https://localhost
5. Category: Application Integration
6. Create → copy Client ID and Client Secret

### 4. Configure the Bot

Open config.py in a text editor (Notepad, VS Code, etc.) and fill in:
```
class ApiKeys:
    PSN_NPSSO = "paste_your_npsso_here"
    DISCORD_TOKEN = "paste_your_discord_token_here"
    IGDB = {
        "client_id": "paste_your_client_id_here",
        "client_secret": "paste_your_client_secret_here",
    }
```
Save the file.
Optional tweaks (also in config.py)
- Change status messages
- Restrict commands to certain channels (ALLOWED_CHANNELS = [channel_id_here])
- Disable invite links in /bot-info (ENABLE_INVITES = False)

### 5. Run the Bot

Back in your terminal (inside v-PSN-bot folder):
```
python main.py
```
You should see:
```
Bot is online!
```
The bot will now appear in your Discord server with rotating statuses.

### 6. Test Commands

Use slash commands in Discord:
- /user-search online_id:YourPSNUsername
- /game-search query:God of War
- /recent-games username:YourPSNUsername
- /bot-info
- /change-language
  
**Avatar group:**
- /avatar verify
- /avatar add_to_cart
- /avatar remove_from_cart


### Common Issues & Fixes

- Bot not responding to commands?
Make sure you invited it with slash command permissions and it's online.
- PSN errors?
Your NPSSO might be expired — get a new one and update config.py.
- IGDB errors?
Double-check Client ID/Secret.
- Private profile data
The bot will show "Private" — that's normal.






