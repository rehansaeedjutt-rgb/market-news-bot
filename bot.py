import feedparser
import requests
import os
import time
import hashlib
import re
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
DB_FILE = "sent_urls.txt"

def get_sent_hashes():
    """Memory read karta hai (Hashes aur URLs dono)."""
    if not os.path.exists(DB_FILE): return set()
    with open(DB_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_sent_hash(identifier):
    """Nayi news ko memory mein save karta hai."""
    with open(DB_FILE, "a") as f:
        f.write(identifier + "\n")

def analyze_market(headline):
    """Coin pehchanta hai aur Market Impact predict karta hai."""
    headline_lower = headline.lower()
    
    # 1. Coin Identification
    coins = {"btc": "Bitcoin (BTC)", "eth": "Ethereum (ETH)", "xrp": "Ripple (XRP)", 
             "sol": "Solana (SOL)", "doge": "Dogecoin", "bnb": "Binance Coin"}
    detected_coin = "General Market"
    for code, name in coins.items():
        if code in headline_lower:
            detected_coin = name
            break

    # 2. Impact Logic (Pump vs Dump)
    if any(word in headline_lower for word in ["surge", "pump", "bullish", "approved", "buying"]):
        impact = "🚀 **BOOST / PUMP** (High Probability)"
        color = 0x2ecc71 # Green
    elif any(word in headline_lower for word in ["dump", "crash", "bearish", "banned", "hack", "drop"]):
        impact = "📉 **DUMP / CRASH** (Warning)"
        color = 0xe74c3c # Red
    else:
        impact = "⚖️ **NEUTRAL** (Sideways Movement)"
        color = 0x3498db # Blue

    return detected_coin, impact, color

def send_to_discord(headline, summary):
    coin, impact, embed_color = analyze_market(headline)
    clean_summary = re.sub('<.*?>', '', summary)[:400] # HTML saaf karna

    payload = {
        "username": "⚓ FUTURE ADMIRAL INTELLIGENCE",
        "embeds": [{
            "title": "📋 ADMIRAL'S MARKET REPORT",
            "color": embed_color,
            "fields": [
                {"name": "📰 News Headline", "value": f"**{headline}**", "inline": False},
                {"name": "📝 Breakdown", "value": clean_summary, "inline": False},
                {"name": "🪙 Asset", "value": coin, "inline": True},
                {"name": "📊 Market Effect", "value": impact, "inline": True}
            ],
            "footer": {"text": "Future Admiral | AI-Driven Market Analysis"},
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }]
    }
    requests.post(WEBHOOK_URL, json=payload)

def fetch_news():
    sent_data = get_sent_hashes()
    feeds = ["https://watcher.guru/news/feed", "https://cointelegraph.com/rss"]
    
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            # Sirf URL nahi, title ka hash bhi check karo (Double Security)
            headline_hash = hashlib.md5(entry.title.encode()).hexdigest()
            
            if entry.link not in sent_data and headline_hash not in sent_data:
                send_to_discord(entry.title, entry.summary)
                save_sent_hash(entry.link)
                save_sent_hash(headline_hash)
                print(f"✅ Sent: {entry.title[:30]}")
                time.sleep(2)

if __name__ == "__main__":
    fetch_news()
