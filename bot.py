import feedparser
import requests
import os
import time
import re
from datetime import datetime
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Environment configuration
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
DB_FILE = os.getenv('DB_FILE', 'sent_urls.txt')

if not WEBHOOK_URL:
    logger.error("ERROR: DISCORD_WEBHOOK not found in .env file")
    exit(1)


def get_memory():
    """Load article history to avoid duplicates"""
    try:
        with open(DB_FILE, 'r') as f:
            urls = f.read().splitlines()
            return urls
    except FileNotFoundError:
        return []


def save_memory(articles):
    """Save processed articles to database"""
    try:
        with open(DB_FILE, 'a') as f:
            for article in articles:
                f.write(article + '\n')
    except IOError as e:
        logger.error(f"Error saving to database: {e}")


def analyze_market_impact(article_title):
    """Analyze market impact with sentiment analysis"""
    article_lower = article_title.lower()
    
    sentiment = {'bullish': 0, 'bearish': 0, 'neutral': 0}
    
    bullish_keywords = ['surge', 'rally', 'jump', 'gain', 'profit', 'positive', 'bull', 'strong', 'rise', 'buy', 'outperform', 'beat', 'tops', 'demand', 'soar']
    bearish_keywords = ['crash', 'plunge', 'fall', 'loss', 'negative', 'bear', 'weak', 'decline', 'sell', 'underperform', 'miss', 'drops', 'hack']
    
    for keyword in bullish_keywords:
        if keyword in article_lower:
            sentiment['bullish'] += 1
    
    for keyword in bearish_keywords:
        if keyword in article_lower:
            sentiment['bearish'] += 1
            
    if sentiment['bullish'] > sentiment['bearish']:
        return "bullish"
    elif sentiment['bearish'] > sentiment['bullish']:
        return "bearish"
    else:
        return "neutral"


def clean_html(raw_html):
    """Remove HTML tags from the summary"""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()


def send_to_discord(title, link, summary, sentiment_type):
    """Send formatted message to Discord in Future Admiral Style"""
    try:
        # Clean and truncate summary
        summary = clean_html(summary)
        short_summary = summary[:350] + '...' if len(summary) > 350 else summary
        
        # Determine styling based on sentiment
        if sentiment_type == "bullish":
            color = 2067276  # Green border
            forecast = "🚀 **PUMP / BOOST** (Positive Market Move)"
        elif sentiment_type == "bearish":
            color = 15158332  # Red border
            forecast = "📉 **DUMP / DROP** (Negative Market Move)"
        else:
            color = 3447003  # Blue border (Neutral)
            forecast = "⚖️ **NEUTRAL** (Stable / Sideways)"
        
        embed_content = {
            'author': {
                'name': "📋 ADMIRAL'S MARKET INTELLIGENCE"
            },
            'title': title,
            'url': link,
            'description': f"📝 **Analysis & Breakdown**\n{short_summary}\n\n[Read More]({link})",
            'fields': [
                {'name': '🪙 Target Asset', 'value': 'Crypto Market', 'inline': True},
                {'name': '📊 Market Forecast', 'value': forecast, 'inline': True}
            ],
            'color': color,
            'footer': {
                'text': f"Future Admiral | Trading & Analysis • {datetime.now().strftime('%m/%d/%Y %I:%M %p')}"
            }
        }
        
        # Set custom username for the bot
        payload = {
            'username': 'FUTURE ADMIRAL INTELLIGENCE',
            'embeds': [embed_content]
        }
        
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        
        if response.status_code in [200, 204]:
            logger.info(f"✅ Successfully sent: {title[:30]}...")
            return True
        else:
            logger.error(f"❌ Failed to send: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False


def start_engine():
    """Main orchestrator function"""
    try:
        processed_articles = get_memory()
        
        # Fetch RSS feed from CoinTelegraph
        logger.info("📡 Fetching market data...")
        feed = feedparser.parse('https://cointelegraph.com/rss')
        
        if not feed.entries:
            logger.warning("⚠️ No entries found in RSS feed")
            return
            
        new_articles = []
        for entry in feed.entries:
            title = entry.title if hasattr(entry, 'title') else 'Unknown'
            link = entry.link if hasattr(entry, 'link') else ''
            
            # Extract summary from feed description
            if hasattr(entry, 'description'):
                summary = entry.description
            elif hasattr(entry, 'summary'):
                summary = entry.summary
            else:
                summary = "No detailed analysis available for this update."
            
            if link not in processed_articles and title:
                new_articles.append({'title': title, 'link': link, 'summary': summary})
        
        if not new_articles:
            logger.info("ℹ️ No new articles found.")
            return
            
        for article in new_articles:
            try:
                sentiment = analyze_market_impact(article['title'])
                send_to_discord(article['title'], article['link'], article['summary'], sentiment)
                time.sleep(2)  # Delay to avoid Discord rate limits
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                continue
        
        # Save processed articles
        links_to_save = [article['link'] for article in new_articles]
        save_memory(links_to_save)
        
        logger.info("✅ Cycle completed")
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

if __name__ == '__main__':
    start_engine()
