evangelions' PSN BotWelcome to my custom Discord bot designed for PlayStation Network (PSN) enthusiasts! This bot lets you query user profiles, check trophies, search for games, view recent plays, and even manage avatars via commands. Built from scratch with Python, it's efficient, user-friendly, and fully open-source under my repo.FeaturesUser Profile Lookup: Get detailed PSN account info, including online ID, trophies, friends count, region, and more.
Trophy Summary: View earned trophies (bronze, silver, gold, platinum) and progress levels.
Game Search: Search for games using IGDB API, including descriptions, genres, media, and similar titles.
Recent Games: Check a user's recently played games with play details.
Avatar Management: Verify, add, or remove avatars from your PSN cart (requires specific cookies).
Bot Info: Display bot details, ping, server list, and credits.
Language Support: Switch between English and French (more can be added).
Customizable: Restrict channels, rotate status messages, and more via config.
Secure & Private: Handles private profiles gracefully; no data logging.

PrerequisitesBefore setting up, you'll need:A Discord account and developer access (for bot token).
A PlayStation Network account (for NPSSO cookie).
Twitch Developer account (for IGDB API keys).
Python 3.8+ installed on your machine.
Git (for cloning the repo).

Setup GuideFollow these steps to get the bot running on your own server or locally.1. Clone the RepositoryDownload the code to your machine:

git clone https://github.com/evangelions/v-PSN-bot.git
cd v-PSN-bot

2. Install DependenciesInstall the required Python packages:

pip install -r requirements.txt

This includes:discord.py: For Discord bot framework.
psnawp: PSN API wrapper.
pycountry: For region handling.
colorthief: For extracting avatar colors.

If you encounter issues (e.g., ModelNotFoundError), reinstall discord.py:

pip uninstall discord.py
pip install discord.py==2.3.2

3. Configure the BotOpen config.py in a text editor and fill in your keys:python

class ApiKeys:
    PSN_NPSSO = "your_psn_npsso_cookie_here"  # Obtain from browser cookies after logging into PSN (see PSNAWP docs).
    DISCORD_TOKEN = "your_discord_bot_token_here"  # From Discord Developer Portal.
    IGDB = {
        "client_id": "your_twitch_client_id_here",
        "client_secret": "your_twitch_client_secret_here",
    }

Discord Token: Create a bot at Discord Developer Portal. Enable all Privileged Gateway Intents (Presence, Server Members, Message Content).
PSN NPSSO: Log into PlayStation.com, open browser dev tools (F12), go to Network tab, refresh, and find the NPSSO cookie value in a request header.
IGDB Keys: Register at Twitch Developers, create an app with OAuth redirect URL as https://localhost.

Other config options:STATUS_MESSAGES: Customize bot status rotations.
ALLOWED_CHANNELS: Restrict commands to specific channel IDs (leave empty for all).
ENABLE_INVITES: Allow invite links in /bot-info (default: True).

4. Run the BotStart the bot:

python main.py

The console should show "Bot is online!".
Invite the bot to your Discord server via the Developer Portal (OAuth2 URL Generator: select bot scope and permissions like Send Messages, Embed Links).
The bot uses slash commands (e.g., /user-search).

If running on a server (e.g., Heroku, VPS), use environment variables for keys and a process manager like PM2.5. Testing CommandsOnce online, test in Discord:/user-search online_id:your_psn_username: Fetch profile details.
/game-search query:game_name: Search for game info.
/recent-games username:psn_username: View recent plays.
/bot-info: Bot stats and credits.
/change-language: Switch languages.
Avatar commands: /avatar verify, /avatar add_to_cart, etc. (ephemeral for privacy).

For owner-only: /toggle-ban, /refresh-psn-token.TroubleshootingAPI Errors: Check keys; refresh NPSSO if expired.
Rate Limits: PSN/IGDB have limits — avoid spam.
Private Profiles: Bot handles forbidden access gracefully.
Dependencies Fail: Ensure Python version matches (3.12+ recommended).
No Commands?: Ensure bot has slash command permissions in server settings.

If issues persist, check console logs or open an issue on this repo.

