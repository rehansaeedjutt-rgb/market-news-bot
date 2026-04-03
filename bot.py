import feedparser
import requests
import os
import time
import hashlib
import re
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
DB_FILE = "sent_urls.txt"

def get_sent_hashes():
    """Memory read karta hai (Hashes) taake repetition na ho."""
    if not os.path.exists(DB_FILE): return set()
    with open(DB_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_sent_hash(h_hash):
    """Nayi news ka hash save karta hai."""
    with open(DB_FILE, "a") as f:
        f.write(h_hash + "\n")

def analyze_intelligence(headline, description):
    """News ko analyze karke Coin aur Impact nikalta hai."""
    combined_text = (headline + " " + description).lower()
    
    # 1. Coin Identification
    coins = {
        "btc": "Bitcoin (BTC)", "eth": "Ethereum (ETH)", "xrp": "Ripple (XRP)", 
        "sol": "Solana (SOL)", "doge": "Dogecoin (DOGE)", "pepe": "PEPE Coin",
        "bnb": "Binance (BNB)", "ada": "Cardano (ADA)"
    }
    detected_coin = "General Crypto Market"
    for code, name in coins.items():
        if code in combined_text:
            detected_coin = name
            break

    # 2. Market Impact (Pump vs Dump)
    if any(word in combined_text for word in ["surge", "pump", "bullish", "moon", "buy", "approved", "green"]):
        impact = "🚀 **PUMP / BOOST** (Positive Momentum Expected)"
        color = 0x2ecc71 # Green
    elif any(word in combined_text for word in ["dump", "crash", "bearish", "dip", "sell", "banned", "hack", "red"]):
        impact = "📉 **DUMP / CRASH** (Caution: Bearish Movement)"
        color = 0xe74c3c # Red
    else:
        impact = "⚖️ **NEUTRAL** (Market Stability / Sideways)"
        color = 0x3498db # Blue

    return detected_coin, impact, color

def send_to_discord(headline, summary):
    coin, impact, embed_color = analyze_intelligence(headline, summary)
    
    # HTML clean karna aur news ko concise banana
    clean_desc = re.sub('<.*?>', '', summary)[:500] 

    payload = {
        "username": "⚓ FUTURE ADMIRAL INTELLIGENCE",
        "avatar_url": "https://i.imgur.com/your-logo.png", # Agar aapka logo hai toh link daalein
        "embeds": [{
            "title": "📋 ADMIRAL'S MARKET INTELLIGENCE",
            "description": f"**{headline}**",
            "color": embed_color,
            "fields": [
                {
                    "name": "📝 Analysis & Breakdown",
                    "value": clean_desc if clean_desc else "Direct market move detected.",
                    "inline": False
                },
                {
                    "name": "🪙 Target Asset",
                    "value": coin,
                    "inline": True
                },
                {
                    "name": "📊 Market Outlook",
                    "value": impact,
                    "inline": True
                }
            ],
            "footer": {
                "text": "⚓ Private Intel | Future Admiral Protocol"
            },
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }]
    }
    requests.post(WEBHOOK_URL, json=payload)

def fetch_news():
    sent_hashes = get_sent_hashes()
    # Sirf top quality feeds
    feeds = ["https://watcher.guru/news/feed", "https://cointelegraph.com/rss"]
    
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]: # Har source se top 3 news
            # Title ka hash banate hain deduplication ke liye
            h_hash = hashlib.md5(entry.title.encode()).hexdigest()
            
            if h_hash not in sent_hashes:
                send_to_discord(entry.title, entry.summary)
                save_sent_hash(h_hash)
                print(f"✅ Intelligence Relayed: {entry.title[:30]}")
                time.sleep(2)

if __name__ == "__main__":
    fetch_news()
