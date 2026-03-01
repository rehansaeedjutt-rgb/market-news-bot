import feedparser
import requests
import os
import time
import concurrent.futures
from dotenv import load_dotenv

# .env file se configurations load karna
load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
DB_FILE = "sent_urls.txt"

def get_sent_urls():
    """Pehle se bheji gayi news ke links read karta hai."""
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r") as f:
        return set(line.strip() for line in f)

def normalize_url(url):
    """Normalize URL by removing query params and trailing slashes."""
    from urllib.parse import urlparse, urlunparse
    parsed = urlparse(url)
    # Remove query string and fragment to avoid duplicate tracking
    normalized = urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip('/'), '', '', ''))
    return normalized

def headline_hash(headline):
    """Create a simple hash of headline for duplicate detection."""
    import hashlib
    return hashlib.md5(headline.lower().strip().encode()).hexdigest()[:16]

def save_sent_url(url):
    """Nayi bheji gayi news ka link save karta hai."""
    with open(DB_FILE, "a") as f:
        f.write(url + "\n")

def send_to_discord(headline, link, source):
    """Branded message send karne ke liye setup."""
    payload = {
        "embeds": [{
            # simple layout: title (📰 News), headline text, footer includes branding
            "title": "📰 News",
            "description": headline,
            "url": link,
            "color": 0x3498db,
            "footer": {
                "text": "Future Admiral | Trading & Analysis"
            },
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }]
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code == 204:
            print(f"Successfully sent branded update: {headline}")
        else:
            print(f"Failed to send to Discord (status {response.status_code}): {response.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"Discord webhook request failed: {e}")

def fetch_market_news():
    sent_urls = get_sent_urls()
    
    # Aapki di gayi websites ki RSS feeds
    feeds = {
        "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "CoinTelegraph": "https://cointelegraph.com/rss",
        "Financial Times": "https://www.ft.com/markets?format=rss",
        "Watcher.guru": "https://watcher.guru/news/feed",
        "The Block": "https://www.theblock.co/rss.xml",
        "Bitcoin Magazine": "https://bitcoinmagazine.com/feed"
    }

    def fetch_and_parse(url):
        """Fetch URL and parse feed. Designed to run inside a worker thread."""
        resp = requests.get(url, timeout=8, headers={
            "User-Agent": "MarketNewsBot/1.0 (+https://github.com/rehansaeedjutt-rgb)"
        })
        resp.raise_for_status()
        return feedparser.parse(resp.content)

    for source, url in feeds.items():
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(fetch_and_parse, url)
                feed = future.result(timeout=12)
        except concurrent.futures.TimeoutError:
            print(f"Timeout fetching/parsing feed {source}")
            continue
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch feed {source}: {e}")
            continue
        except Exception as e:
            print(f"Error parsing feed {source}: {e}")
            continue

        if getattr(feed, 'entries', None):
            latest = feed.entries[0]
            normalized_link = normalize_url(latest.link)
            headline_id = headline_hash(latest.title)
            
            # Check if this news is new (by URL or headline)
            is_duplicate = normalized_link in sent_urls or headline_id in sent_urls
            
            if not is_duplicate:
                send_to_discord(latest.title, latest.link, source)
                # Save both normalized URL and headline hash for dedup
                save_sent_url(normalized_link)
                save_sent_url(headline_id)
                print(f"New Alert Sent: {latest.title}")
            else:
                print(f"Skipping old news: {latest.title}")
        time.sleep(1)

if __name__ == "__main__":
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK environment variable is not set.")
    else:
        fetch_market_news()