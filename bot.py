import os
from dotenv import load_dotenv

load_dotenv()  # Ye line .env file se data uthati hai
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
import feedparser
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
DB_FILE = "sent_urls.txt"

def get_sent_urls():
    """Pehle se bheji gayi news ke links read karta hai."""
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_sent_url(url):
    """Nayi bheji gayi news ka link save karta hai."""
    with open(DB_FILE, "a") as f:
        f.write(url + "\n")

def send_to_discord(title, link, source):
    payload = {
        "embeds": [{
            "title": f"🚀 {source} Update",
            "description": title,
            "url": link,
            "color": 0x3498db
        }]
    }
    requests.post(WEBHOOK_URL, json=payload)

def fetch_market_news():
    sent_urls = get_sent_urls()
    feeds = {
        "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "CoinTelegraph": "https://cointelegraph.com/rss",
        "Financial Times": "https://www.ft.com/markets?format=rss"
    }

    for source, url in feeds.items():
        feed = feedparser.parse(url)
        if feed.entries:
            latest = feed.entries[0]
            # Check if this news is new
            if latest.link not in sent_urls:
                send_to_discord(latest.title, latest.link, source)
                save_sent_url(latest.link)
                print(f"New Alert Sent: {latest.title}")
            else:
                print(f"Skipping old news: {latest.title}")
            time.sleep(1)

if __name__ == "__main__":
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK is not set.")
    else:
        fetch_market_news()