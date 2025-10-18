# SIFF Calendar Scraper

Scrapes events from SIFF.net (Seattle International Film Festival) calendar and generates iCal feeds.

## Disclaimer

**This is an independent, unofficial project and is not affiliated with, endorsed by, or connected to the Seattle International Film Festival (SIFF) or SIFF.net in any way.** This is a personal project created for convenience to make SIFF's publicly available calendar data easier to consume in standard calendar applications. All event data is sourced from the public SIFF.net website.

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
python -m src.main

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
- `output/index.html` (status page)

## Deployment

This project uses GitHub Actions to scrape the calendar nightly and publish to GitHub Pages.

### Setup

1. Enable GitHub Pages in repository settings:
   - Settings > Pages
   - Source: GitHub Actions

2. The workflow runs automatically at 2 AM UTC daily

3. Manual trigger: Actions tab > "Scrape SIFF Calendar" > "Run workflow"

### Access Feeds

After deployment, calendars are available at:
- `https://leftathome.github.io/siffscrape/` (status page with links)
- `https://leftathome.github.io/siffscrape/siff-all.ics`
- `https://leftathome.github.io/siffscrape/siff-programming-only.ics`
- `https://leftathome.github.io/siffscrape/siff-downtown.ics`
- `https://leftathome.github.io/siffscrape/siff-uptown.ics`
- `https://leftathome.github.io/siffscrape/siff-film-center.ics`

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
