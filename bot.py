import feedparser
import requests
import os
import time
import hashlib
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

# Environment configuration with validation
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
COMPANY_NAME = os.getenv('COMPANY_NAME', 'Market Bot')
TIMEZONE = os.getenv('TIMEZONE', 'UTC')
DB_FILE = os.getenv('DB_FILE', 'sent_urls.txt')

# Validate required environment variables
if not WEBHOOK_URL:
    logger.error("ERROR: DISCORD_WEBHOOK not found in .env file")
    exit(1)


def get_memory():
    """Load article history to avoid duplicates"""
    try:
        with open(DB_FILE, 'r') as f:
            urls = f.read().splitlines()
            logger.info(f"Loaded {len(urls)} previously processed articles")
            return urls
    except FileNotFoundError:
        logger.warning(f"Database file {DB_FILE} not found. Creating new one.")
        return []


def save_memory(articles):
    """Save processed articles to database"""
    try:
        with open(DB_FILE, 'a') as f:
            for article in articles:
                f.write(article + '\n')
        logger.info(f"Saved {len(articles)} new articles to database")
    except IOError as e:
        logger.error(f"Error saving to database: {e}")


def analyze_market_impact(article_title):
    """Analyze market impact with sentiment analysis"""
    article_lower = article_title.lower()
    
    sentiment = {'bullish': 0, 'bearish': 0, 'neutral': 0}
    
    # Bullish keywords
    bullish_keywords = ['surge', 'rally', 'jump', 'gain', 'profit', 'positive', 'bull', 'strong', 'rise', 'buy', 'outperform', 'beat']
    # Bearish keywords
    bearish_keywords = ['crash', 'plunge', 'fall', 'loss', 'negative', 'bear', 'weak', 'decline', 'sell', 'underperform', 'miss']
    
    for keyword in bullish_keywords:
        if keyword in article_lower:
            sentiment['bullish'] += 1
    
    for keyword in bearish_keywords:
        if keyword in article_lower:
            sentiment['bearish'] += 1
    
    # Calculate confidence score
    total_sentiment = sum(sentiment.values())
    if total_sentiment == 0:
        sentiment['neutral'] = 1
        confidence = 0
    else:
        confidence = 100 * (sentiment['bullish'] - sentiment['bearish']) / max(1, total_sentiment)
    
    # Determine sentiment label
    if sentiment['bullish'] > sentiment['bearish']:
        sentiment_label = '📈 Bullish'
    elif sentiment['bearish'] > sentiment['bullish']:
        sentiment_label = '📉 Bearish'
    else:
        sentiment_label = '➡️ Neutral'
    
    return sentiment, confidence, sentiment_label


def send_to_discord(executive_summary, asset_class, sentiment_analysis, signal_strength, sentiment_label):
    """Send formatted message to Discord"""
    try:
        # Truncate summary if too long
        summary = executive_summary[:2000] if len(executive_summary) > 2000 else executive_summary
        
        # Determine embed color based on sentiment
        if signal_strength > 30:
            color = 3066993  # Green (bullish)
        elif signal_strength < -30:
            color = 15158332  # Red (bearish)
        else:
            color = 9807270  # Orange (neutral)
        
        embed_content = {
            'title': f'🔔 {COMPANY_NAME} - Market Update',
            'description': summary,
            'fields': [
                {'name': '📊 Asset Class', 'value': asset_class, 'inline': True},
                {'name': '💡 Sentiment', 'value': sentiment_label, 'inline': True},
                {'name': '📈 Signal Strength', 'value': f"{signal_strength:.1f}%", 'inline': True},
                {'name': '⏰ Timestamp', 'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'inline': False},
            ],
            'color': color,
            'footer': {'text': f'{COMPANY_NAME} | {TIMEZONE}'}
        }
        
        payload = {'embeds': [embed_content]}
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        
        if response.status_code == 204:
            logger.info(f"✅ Successfully sent to Discord: {executive_summary[:50]}...")
            return True
        else:
            logger.error(f"❌ Failed to send to Discord: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Request error sending to Discord: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False


def start_engine():
    """Main orchestrator function"""
    try:
        logger.info("=" * 60)
        logger.info("🚀 Starting Market Intelligence Bot")
        logger.info("=" * 60)
        
        # Load processed articles
        processed_articles = get_memory()
        
        # Fetch RSS feed
        logger.info("📡 Fetching market data from RSS feed...")
        feed = feedparser.parse('https://finance.yahoo.com/rss/2.0/headline')
        
        if not feed.entries:
            logger.warning("⚠️ No entries found in RSS feed")
            return
        
        logger.info(f"📰 Found {len(feed.entries)} articles in feed")
        
        # Filter new articles
        new_articles = []
        for entry in feed.entries:
            title = entry.title if hasattr(entry, 'title') else 'Unknown'
            link = entry.link if hasattr(entry, 'link') else ''
            
            if link not in processed_articles and title:
                new_articles.append({'title': title, 'link': link})
        
        if not new_articles:
            logger.info("ℹ️ No new articles found.")
            return
        
        logger.info(f"✨ Found {len(new_articles)} new articles!")
        
        # Process and send new articles
        for article in new_articles:
            try:
                title = article['title']
                link = article['link']
                
                sentiment, confidence, sentiment_label = analyze_market_impact(title)
                
                # Send to Discord
                send_to_discord(
                    executive_summary=f"**{title}**\n\n[Read More]({link})",
                    asset_class='Finance/Markets',
                    sentiment_analysis=sentiment,
                    signal_strength=confidence,
                    sentiment_label=sentiment_label
                )
                
                # Add small delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                continue
        
        # Save processed articles
        links_to_save = [article['link'] for article in new_articles]
        save_memory(links_to_save)
        
        logger.info("=" * 60)
        logger.info("✅ Bot cycle completed successfully")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Fatal error in start_engine: {e}")


if __name__ == '__main__':
    start_engine()
