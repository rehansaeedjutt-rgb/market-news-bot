import feedparser
import requests
import os
import time
import concurrent.futures
import re # For cleaning HTML tags
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
DB_FILE = "sent_urls.txt"
LOOP_INTERVAL = 600 

def clean_html(raw_html):
    """Removes HTML tags from RSS descriptions for a clean look."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def get_sent_urls():
    if not os.path.exists(DB_FILE): return set()
    with open(DB_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_sent_url(url):
    with open(DB_FILE, "a") as f:
        f.write(url + "\n")

def analyze_impact(headline):
    """
    A simple logic to guess impact. 
    In the future, you can replace this with an actual AI API call.
    """
    headline_lower = headline.lower()
    if any(word in headline_lower for word in ["surge", "pump", "adoption", "buy", "bullish", "approved"]):
        return "🟢 **BULLISH** (Likely Price Increase)"
    elif any(word in headline_lower for word in ["hack", "crash", "dump", "banned", "lawsuit", "bearish"]):
        return "🔴 **BEARISH** (Potential Price Drop)"
    else:
        return "🟡 **NEUTRAL** (Market Stability)"

def send_branded_analysis(headline, description, source):
    """Sends the news with Analysis and Impact, NO clickable website button."""
    
    clean_desc = clean_html(description)[:500] # Keep it concise
    impact = analyze_impact(headline)

    # Creating a professional text-based report
    payload = {
        "username": "⚓ FUTURE ADMIRAL INTELLIGENCE",
        "embeds": [{
            "title": f"📋 ADMIRAL'S MARKET REPORT",
            "color": 0x2c3e50, # Dark professional grey
            "fields": [
                {
                    "name": "📰 The News",
                    "value": f"**{headline}**",
                    "inline": False
                },
                {
                    "name": "📝 Breakdown",
                    "value": clean_desc if clean_desc else "No detailed summary provided.",
                    "inline": False
                },
                {
                    "name": "📈 Market Impact",
                    "value": impact,
                    "inline": True
                },
                {
                    "name": "🏛️ Source",
                    "value": source,
                    "inline": True
                }
            ],
            "footer": {
                "text": "Future Admiral | Proprietary Analysis Engine"
            },
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }]
    }

    try:
        # We REMOVED the "url" field from the embed so no website button appears
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code == 204:
            print(f"✅ Analysis Sent: {headline[:30]}...")
    except Exception as e:
        print(f"⚠️ Webhook Error: {e}")

def fetch_market_news():
    print(f"\n--- 📡 Processing Intelligence ({time.strftime('%H:%M:%S')}) ---")
    sent_urls = get_sent_urls()
    
    feeds = {
        "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "Watcher Guru": "https://watcher.guru/news/feed",
        "The Block": "https://www.theblock.co/rss.xml"
    }

    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                latest = feed.entries[0]
                if latest.link not in sent_urls:
                    # Logic: We send the Title and the Summary (Description)
                    send_branded_analysis(latest.title, latest.summary, source)
                    save_sent_url(latest.link)
                else:
                    print(f"⏭️ Already analyzed: {latest.title[:30]}...")
        except Exception as e:
            print(f"⚠️ Error fetching {source}: {e}")
        time.sleep(2)

if __name__ == "__main__":
    print("⚓ FUTURE ADMIRAL ANALYTICS IS LIVE")
    while True:
        fetch_market_news()
        print(f"💤 Analyzing market trends... (Next check in 10m)")
        time.sleep(LOOP_INTERVAL)
