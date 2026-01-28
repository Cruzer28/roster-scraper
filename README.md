# Sports Roster Scraper

Automated tool for scraping college sports roster data from athletic websites.

## Features

- **Multi-Method Input**: Scrape directly from URLs or paste HTML for JS-heavy sites
- **Platform Support**: Handles Sidearm Sports, Presto Sports, and generic sites
- **Live Preview & Editing**: Review and correct data before export
- **CSV Export**: Matches your existing spreadsheet format
- **Team Collaboration**: Simple web interface anyone can use

## Quick Start

### Local Setup (Testing)

1. **Install dependencies:**
```bash
cd roster_scraper
pip install -r requirements.txt
```

2. **Run the app:**
```bash
python app.py
```

3. **Open in browser:**
```
http://localhost:5000
```

## Usage Guide

### Method 1: Direct URL Scraping (Simpler Sites)

1. Find the roster page URL (e.g., `https://okstate.com/sports/mens-basketball/roster`)
2. Paste it in the "Scrape from URL" tab
3. Click "Scrape Roster"
4. Review, edit if needed, and export

### Method 2: HTML Paste (JS-Heavy Sites)

For sites that don't work with direct scraping:

1. Go to the roster page in your browser
2. Right-click → "View Page Source" (or Ctrl+U / Cmd+U)
3. Select All (Ctrl+A / Cmd+A) and Copy
4. Switch to "Paste HTML" tab
5. Paste the URL (for image links)
6. Paste the HTML content
7. Click "Parse HTML"
8. Review, edit if needed, and export

### Editing Data

- All fields are editable - just click and type
- Delete players/coaches with the Delete button
- Changes save automatically
- Update team name at the top

## Deployment Options

### Option 1: Render.com (Recommended)

**Free tier available, $7/month for always-on**

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. New → Web Service
4. Connect your repo
5. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `python app.py`
6. Deploy!

### Option 2: Railway

**$5 free credit/month**

1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. New Project → Deploy from GitHub
4. Select your repo
5. Railway auto-detects Python and deploys

### Option 3: Fly.io

**Good free tier**

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy
cd roster_scraper
fly launch
fly deploy
```

## Platform Support

### Currently Supported:
- ✅ Sidearm Sports (OK State, many D1 schools)
- ✅ Presto Sports
- ✅ Generic HTML tables

### Coming Soon:
- SIDEARM Roster Module (enhanced)
- NCAA.com rosters
- Conference websites

## Customization

### Adding New Platforms

Edit `scraper.py` and add a new parser method:

```python
def _parse_new_platform(self, soup, url):
    roster_data = {
        'team_name': '',
        'coaches': [],
        'players': []
    }
    # Your parsing logic here
    return roster_data
```

Then update `scrape_from_html()` to detect and use it.

### Changing CSV Format

Edit the `export_csv()` function in `app.py` to match your exact spreadsheet layout.

## Troubleshooting

### No Players Found
- Try the HTML paste method
- Some sites require JavaScript - the HTML paste gets the rendered content
- Check if site structure changed

### Missing Images
- Make sure you paste the page URL in HTML paste method
- Some images may be behind authentication
- You can manually add image URLs in the preview

### Wrong Data Extracted
- Use the preview editor to correct fields
- Report the site URL so we can improve the parser
- Save your corrections and export

## Future Enhancements

- [ ] Google Sheets direct integration
- [ ] Browser extension for one-click scraping
- [ ] Coaching staff bio scraping
- [ ] Player stats integration
- [ ] Batch processing multiple teams
- [ ] Photo downloading and hosting

## Contributing

Found a site that doesn't work? Open an issue with:
1. The roster page URL
2. Screenshot of what you're seeing
3. What data is missing/wrong

## License

MIT - Do whatever you want with it!

---

**Need help?** Ping Cruz or check the issues page on GitHub.
