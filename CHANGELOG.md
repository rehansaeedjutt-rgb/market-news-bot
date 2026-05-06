# Changelog

## [1.1.0] - 2026-05-06

### 🐛 Fixed
- **Environment Variable Bug**: Changed `WEBHOOK_URL` to `DISCORD_WEBHOOK` to match .env file
- **Error Handling**: Added comprehensive try-catch blocks for all network operations
- **Sentiment Analysis**: Replaced simple string matching with 12+ keyword detection
- **Discord API**: Fixed HTTP response validation (now checks for 204 status code)
- **Database Operations**: Added exception handling for file I/O errors
- **Rate Limiting**: Added 1-second delay between Discord messages to prevent throttling

### ✨ Added
- **Logging System**: Complete logging with timestamps and log levels (INFO, WARNING, ERROR)
- **Environment Validation**: Checks for required variables on startup
- **Color-Coded Embeds**: Discord messages now show different colors based on sentiment
  - 🟢 Green: Bullish (confidence > 30%)
  - 🔴 Red: Bearish (confidence < -30%)
  - 🟠 Orange: Neutral
- **Better Sentiment Labels**: Shows emoji-based sentiment indicators
- **Request Timeout**: Set 10-second timeout for all Discord requests
- **Improved Summary**: Truncates long article titles to 2000 characters for Discord
- **Better Feed Parsing**: Now uses proper RSS feed entry attributes

### 📝 Documentation
- Added `TROUBLESHOOTING.md` with 5 common errors and solutions
- Updated `.env.example` with detailed comments
- Added version pins to `requirements.txt` for stability

### 🔧 Configuration
- Default DB_FILE: `sent_urls.txt`
- Default COMPANY_NAME: `Market Bot`
- Default TIMEZONE: `UTC`
- Request timeout: 10 seconds
- Rate limit delay: 1 second between messages

---

## [1.0.0] - 2026-02-28

### Initial Release
- Basic RSS feed parsing from Yahoo Finance
- Duplicate detection using article history
- Simple sentiment analysis
- Discord webhook integration
- Article history storage in text file
