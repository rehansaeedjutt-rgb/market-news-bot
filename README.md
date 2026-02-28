# market-news-bot

A simple script that fetches market news from RSS feeds and sends updates to a Discord channel via a webhook.

## Setup

1. **Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Environment variable**
   - Create a Discord webhook and set `DISCORD_WEBHOOK` before running the bot:
     ```bash
     export DISCORD_WEBHOOK="https://discord.com/api/webhooks/...."
     ```

3. **Run**
   ```bash
   python bot.py
   ```

