import feedparser
import requests
import os
import time
import hashlib
import re
from dotenv import load_dotenv

# Environment variables load karna
load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
DB_FILE = "sent_urls.txt"

def get_memory():
    if not os.path.exists(DB_FILE): return set()
    with open(DB_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_memory(identifier):
    with open(DB_FILE, "a") as f:
        f.write(identifier + "\n")

def analyze_market_impact(text):
    text = text.lower()
    # 1. Coin Identification
    coins = {"btc": "Bitcoin", "eth": "Ethereum", "xrp": "Ripple", "sol": "Solana", "doge": "Dogecoin"}
    target = "Crypto Market"
    for code, name in coins.items():
        if code in text:
            target = name
            break
            
    # 2. Pump/Dump Prediction Logic
    if any(w in text for w in ["surge", "pump", "bullish", "approved", "buy", "growth"]):
        impact = "🚀 **PUMP / BOOST** (Positive Market Move)"
        color = 0x2ecc71 # Green
    elif any(w in text for w in ["crash", "dump", "bearish", "hack", "drop", "sell"]):
        impact = "📉 **DUMP / CRASH** (Negative Market Move)"
        color = 0xe74c3c # Red
    else:
        impact = "⚖️ **NEUTRAL** (Stable / Sideways)"
        color = 0x3498db # Blue
        
    return target, impact, color

def send_to_discord(headline, summary):
    target, impact, color = analyze_market_impact(headline + " " + summary)
    # HTML saaf karke summary ko chota karna
    clean_desc = re.sub('<.*?>', '', summary)[:400]

    payload = {
        "username": "⚓ FUTURE ADMIRAL INTELLIGENCE",
        "embeds": [{
            "title": "📋 ADMIRAL'S MARKET INTELLIGENCE",
            "description": f"### {headline}",
            "color": color,
            "fields": [
                {"name": "📝 Analysis & Breakdown", "value": clean_desc if clean_desc else "Market movement detected."},
                {"name": "🪙 Target Asset", "value": target, "inline": True},
                {"name": "📊 Market Forecast", "value": impact, "inline": True}
            ],
            "footer": {"text": "Future Admiral | Trading & Analysis"},
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }]
    }
    r = requests.post(WEBHOOK_URL, json=payload)
    return r.status_code

def start_engine():
    print("📡 Admiral Engine Starting...")
    memory = get_memory()
    # Multiple sources for better testing
    feeds = ["https://watcher.guru/news/feed", "https://cointelegraph.com/rss"]
    
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            # News ka unique ID (Headline Hash)
            news_id = hashlib.md5(entry.title.encode()).hexdigest()
            
            if news_id not in memory:
                status = send_to_discord(entry.title, entry.summary)
                if status == 204:
                    save_memory(news_id)
                    print(f"✅ News Sent: {entry.title[:30]}")
                else:
                    print(f"❌ Webhook Error: {status}")
                time.sleep(2)
            else:
                print(f"⏭️ Skipping (Already in memory): {entry.title[:30]}")

if __name__ == "__main__":
    start_engine()
