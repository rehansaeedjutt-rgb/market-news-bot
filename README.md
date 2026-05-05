# Market Intelligence Bot

**Professional Daily Market Update Service**

A sophisticated automation tool designed for institutional market analysis and real-time updates via Discord. This service aggregates market news from premium RSS feeds and delivers actionable insights with professional sentiment analysis.

---

## 📊 Features

- **Real-Time Market Monitoring**: Continuous feeds from leading financial news sources
- **Sentiment Analysis**: Bullish, Bearish, and Neutral sentiment classification
- **Multi-Asset Support**: Crypto, Equities, Commodities, and Forex coverage
- **Duplicate Detection**: Intelligent filtering to prevent redundant updates
- **Professional Formatting**: Institutional-grade Discord embed messages
- **Customizable Company Branding**: White-label support for institutional deployment
- **Time Zone Support**: Global operation capabilities

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- Discord Server with Webhook permissions
- Active internet connection

### Installation Steps

#### 1. Clone & Environment Setup
```bash
git clone https://github.com/rehansaeedjutt-rgb/market-news-bot.git
cd market-news-bot
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Configure Environment Variables
Create a `.env` file in the project root:

```env
# Discord Webhook URL (Required)
DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN

# Company Configuration (Optional)
COMPANY_NAME=RGB Capital Group
TIMEZONE=UTC
```

**How to Create Discord Webhook:**
1. Go to your Discord Server → Settings → Integrations → Webhooks
2. Click "New Webhook"
3. Copy the Webhook URL
4. Set it as `DISCORD_WEBHOOK` in your `.env` file

#### 3. Run the Service
```bash
# One-time execution
python bot.py

# Or schedule with cron (Linux/Mac)
*/30 * * * * cd /path/to/market-news-bot && python bot.py

# Or use Windows Task Scheduler for scheduled runs
```

---

## 📋 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DISCORD_WEBHOOK` | Discord webhook URL | `https://discord.com/api/webhooks/...` |
| `COMPANY_NAME` | Organization name for branding | `RGB Capital Group` |
| `TIMEZONE` | Timezone for timestamps | `UTC`, `EST`, `GMT` |

---

## 📡 Data Sources

The bot monitors the following premium feeds:
- **Watcher.guru** - Crypto market intelligence
- **Cointelegraph** - Blockchain & crypto news
- **CNBC** - General financial markets

---

## 🔍 How It Works

1. **Feed Aggregation**: Fetches latest articles from configured RSS sources
2. **Duplicate Prevention**: Uses MD5 hashing to track processed articles
3. **Sentiment Analysis**: Analyzes headlines for market sentiment
4. **Market Classification**: Identifies target asset (crypto, equities, etc.)
5. **Discord Publication**: Sends formatted embeds with analysis
6. **Memory Management**: Maintains history in `sent_urls.txt`

---

## 📊 Message Format

Each market update includes:
- **Executive Summary**: Article preview
- **Asset Class**: Target market (Bitcoin, S&P 500, etc.)
- **Market Sentiment**: Bullish/Bearish/Neutral classification
- **Professional Footer**: Company branding and timestamp

---

## 🛠️ Development & Customization

### Modify Market Indicators
Edit the `analyze_market_impact()` function in `bot.py` to add:
- Custom asset classes
- Additional sentiment keywords
- Custom color schemes

### Add Data Sources
Update the `feeds` list in `start_engine()`:
```python
feeds = [
    "https://your-feed-url/rss",
    "https://another-feed/feed"
]
```

### Customize Discord Messages
Modify the payload structure in `send_to_discord()` to adjust:
- Embed colors
- Field names and values
- Company avatar and branding

---

## 📦 Requirements

- `feedparser` - RSS feed parsing
- `requests` - HTTP requests
- `python-dotenv` - Environment variable management

See `requirements.txt` for full dependencies.

---

## 🔒 Security Notes

- **Never commit `.env` file** to version control
- Use environment variables for sensitive data
- Restrict webhook access to trusted systems
- Rotate Discord webhooks periodically

---

## 📞 Support & Customization

For institutional deployment, custom modifications, or integration with your trading systems:
- Contact: [Your Contact Info]
- Customization available for: Alert thresholds, multi-channel distribution, API integrations

---

## 📄 License

This project is open-source and available for institutional use.

---

**Version**: 1.0.0  
**Last Updated**: May 2026  
**Status**: Production Ready