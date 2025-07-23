# Telegram User Tagger Bot

A bot that allows admins to assign tags to users in Telegram groups.

## Features
- Assign custom tags to users
- Display tags when users are mentioned
- Simple admin interface
- Persistent tag storage

## Setup
1. Get a bot token from [@BotFather](https://t.me/BotFather)
2. Replace `YOUR_BOT_TOKEN` in `tagger_bot.py`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the bot: `python tagger_bot.py`

## Commands
- `/start` - Show bot info
- `/taguser` (admin only) - Tag a user (reply to their message)
- `/mytags` - Show your current tags

## Customization
Edit the `AVAILABLE_TAGS` dictionary in `tagger_bot.py` to change available tags.