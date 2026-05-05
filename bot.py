import feedparser
import requests
import os
import time
import hashlib
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
COMPANY_NAME = os.getenv('COMPANY_NAME')
TIMEZONE = os.getenv('TIMEZONE')
DB_FILE = os.getenv('DB_FILE')

# Function to load article history to avoid duplicates
def get_memory():
    try:
        with open(DB_FILE, 'r') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []

# Function to save processed articles
def save_memory(articles):
    with open(DB_FILE, 'a') as f:
        for article in articles:
            f.write(article + '\n')

# Function to analyze market impact with institutional sentiment analysis
def analyze_market_impact(article):
    sentiment = {'bullish': 0, 'bearish': 0, 'neutral': 0}
    # Perform sentiment analysis (placeholder - enhance logic with NLP library)
    if 'positive' in article:
        sentiment['bullish'] += 1
    elif 'negative' in article:
        sentiment['bearish'] += 1
    else:
        sentiment['neutral'] += 1

    confidence = 100 * (sentiment['bullish'] - sentiment['bearish']) / max(1, sum(sentiment.values()))
    return sentiment, confidence

# Function to send data to Discord with professional embed formatting
def send_to_discord(executive_summary, asset_class, sentiment_analysis, signal_strength):
    embed_content = {
        'title': COMPANY_NAME + ' Market Update',
        'description': executive_summary,
        'fields': [
            {'name': 'Asset Class', 'value': asset_class},
            {'name': 'Sentiment Analysis', 'value': str(sentiment_analysis)},
            {'name': 'Signal Strength', 'value': str(signal_strength)},
        ],
        'color': 3066993  # professional color code example
    }
    requests.post(WEBHOOK_URL, json={'embeds': [embed_content]})

# Main orchestrator function
def start_engine():
    articles = get_memory()
    feed = feedparser.parse('https://finance.yahoo.com/rss/')
    new_articles = [entry.title for entry in feed.entries if entry.title not in articles]
    if new_articles:
        for article in new_articles:
            sentiment, confidence = analyze_market_impact(article)
            send_to_discord(article, 'Finance', sentiment, confidence)
        save_memory(new_articles)
    else:
        print('No new articles found.')

if __name__ == '__main__':
    start_engine()