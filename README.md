# SIFF Calendar Scraper

Scrapes events from SIFF.net calendar and generates iCal feeds.

## Features

- Scrapes SIFF.net calendar for all venues
- Generates separate iCal feeds per venue
- Provides combined feed of all events
- Special feed for SIFF-curated programming only (excludes first-run releases)
- Status page with scrape statistics
- Respectful rate limiting and caching
- Automated nightly updates via GitHub Actions

## Usage

```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run scraper
python src/main.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## Output

- `output/siff-downtown.ics`
- `output/siff-uptown.ics`
- `output/siff-film-center.ics`
- `output/siff-all.ics`
- `output/siff-programming-only.ics`
- `output/status.html`

## Deployment

This project uses GitHub Actions to scrape the calendar nightly and publish to GitHub Pages.

### Setup

1. Enable GitHub Pages in repository settings:
   - Settings > Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages`, folder: `/ (root)`

2. The workflow runs automatically at 2 AM UTC daily

3. Manual trigger: Actions tab > "Scrape SIFF Calendar" > "Run workflow"

### Access Feeds

After deployment, calendars are available at:
- `https://YOUR-USERNAME.github.io/siffscrape/siff-all.ics`
- `https://YOUR-USERNAME.github.io/siffscrape/siff-programming-only.ics`
- `https://YOUR-USERNAME.github.io/siffscrape/siff-downtown.ics`
- `https://YOUR-USERNAME.github.io/siffscrape/siff-uptown.ics`
- `https://YOUR-USERNAME.github.io/siffscrape/siff-film-center.ics`
- `https://YOUR-USERNAME.github.io/siffscrape/status.html`

## Architecture

- `src/models.py` - Data models (Event, Venue)
- `src/http_client.py` - HTTP client with caching and rate limiting
- `src/calendar_parser.py` - Parse daily calendar pages
- `src/detail_parser.py` - Parse event detail pages
- `src/scraper.py` - Main scraper orchestration
- `src/ical_generator.py` - Generate iCal feeds
- `src/status_page.py` - Generate status HTML page
- `src/main.py` - Entry point

## Contributing

Contributions welcome! Please:
1. Write tests for new features
2. Follow existing code style
3. Update documentation

## License

MIT License - see LICENSE file
