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
python src/scraper.py

# Run tests
pytest
```

## Output

- `output/siff-downtown.ics`
- `output/siff-uptown.ics`
- `output/siff-film-center.ics`
- `output/siff-all.ics`
- `output/siff-programming-only.ics`
- `output/status.html`
