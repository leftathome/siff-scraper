# SIFF Calendar Scraper

Scrapes events from SIFF.net calendar and generates iCal feeds.

## Features

- Per-venue iCal feeds (Downtown, Uptown, Film Center)
- Combined all-events feed
- SIFF-curated programming only feed
- Status page with scrape statistics
- Respects rate limits with caching

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
