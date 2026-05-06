# Troubleshooting Guide

## Common Issues & Solutions

### 1. **Error: `DISCORD_WEBHOOK not found in .env file`**
**Problem:** The bot won't start
**Solution:** 
- Create a `.env` file in the project root (copy from `.env.example`)
- Make sure `DISCORD_WEBHOOK=` is set correctly
- Verify your Discord webhook URL is valid
- Ensure the webhook hasn't been deleted

### 2. **Error: `Failed to send to Discord: HTTP 401`**
**Problem:** Discord webhook authentication failed
**Solution:**
- Regenerate the webhook in Discord (delete and create new one)
- Copy the new URL to `.env`
- Check that the webhook still has permissions

### 3. **Error: `FileNotFoundError: [Errno 2] No such file or directory: 'sent_urls.txt'`**
**Problem:** Database file doesn't exist
**Solution:**
- This is normal on first run - the bot will create it automatically
- If it persists, check file permissions in the directory

### 4. **No articles being sent**
**Problem:** Bot runs but no Discord messages appear
**Solutions:**
- Check RSS feed is working: `feedparser.parse('https://finance.yahoo.com/rss/2.0/headline')`
- Verify webhook URL is correct
- Check Discord channel permissions
- Look at console logs for error messages
- Try removing `sent_urls.txt` to reset processed articles

### 5. **Error: `ModuleNotFoundError: No module named 'feedparser'`**
**Problem:** Missing dependencies
**Solution:**
```bash
pip install -r requirements.txt
```

### 6. **Error: `requests.exceptions.ConnectionError`**
**Problem:** Network connectivity issue
**Solution:**
- Check internet connection
- Verify firewall isn't blocking Discord API
- Try running again after a few seconds

### 7. **Bot running but showing duplicate articles**
**Problem:** Same articles sent multiple times
**Solution:**
- Delete `sent_urls.txt` file to reset
- Next run will be marked as new

## Output Format

When running correctly, you should see:

```
2026-05-06 10:30:45,123 - INFO - ============================================================
2026-05-06 10:30:45,124 - INFO - 🚀 Starting Market Intelligence Bot
2026-05-06 10:30:45,125 - INFO - ============================================================
2026-05-06 10:30:46,234 - INFO - 📡 Fetching market data from RSS feed...
2026-05-06 10:30:47,456 - INFO - 📰 Found 20 articles in feed
2026-05-06 10:30:47,457 - INFO - Loaded 50 previously processed articles
2026-05-06 10:30:47,789 - INFO - ✨ Found 3 new articles!
2026-05-06 10:30:48,901 - INFO - ✅ Successfully sent to Discord: Bitcoin surge rally...
2026-05-06 10:30:49,234 - INFO - ✅ Successfully sent to Discord: Market analysis positive...
2026-05-06 10:30:50,567 - INFO - ✅ Successfully sent to Discord: Crypto gains momentum...
2026-05-06 10:30:50,890 - INFO - Saved 3 new articles to database
2026-05-06 10:30:50,891 - INFO - ============================================================
2026-05-06 10:30:50,892 - INFO - ✅ Bot cycle completed successfully
2026-05-06 10:30:50,893 - INFO - ============================================================
```

## Debug Mode

To see detailed debug information, modify `bot.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## Quick Checklist

- [ ] `.env` file created and filled
- [ ] `DISCORD_WEBHOOK` is set correctly
- [ ] Requirements installed: `pip install -r requirements.txt`
- [ ] Python 3.8+ installed
- [ ] Discord webhook has message permissions
- [ ] Internet connection working
- [ ] No firewall blocking Discord API

## Still Having Issues?

1. Check the `.env` file format (no quotes around values)
2. Run `python -c "import feedparser; print(feedparser.__version__)"` to verify feedparser works
3. Test Discord webhook manually:
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"content":"Test"}' YOUR_WEBHOOK_URL
   ```
4. Check console output for specific error messages
5. Verify RSS feed is accessible by visiting the URL in browser
