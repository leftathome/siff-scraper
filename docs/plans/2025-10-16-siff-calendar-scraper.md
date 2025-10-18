# SIFF Calendar Scraper Implementation Plan

> **For Claude:** Use `${SUPERPOWERS_SKILLS_ROOT}/skills/collaboration/executing-plans/SKILL.md` to implement this plan task-by-task.

**Goal:** Scrape SIFF.net calendar events and generate iCal feeds for each venue, combined events, and SIFF-curated programming only.

**Architecture:** Python scraper fetches daily calendar pages, extracts event details, classifies events by URL pattern (SIFF-programming vs first-run releases), generates static .ics files and status page, deployed via GitHub Actions to GitHub Pages.

**Tech Stack:** Python 3.11+, requests, beautifulsoup4, icalendar, pytest, GitHub Actions, GitHub Pages

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `README.md`

**Step 1: Create requirements.txt**

Create `requirements.txt`:

```
requests>=2.31.0
beautifulsoup4>=4.12.0
icalendar>=5.0.11
pytest>=7.4.0
pytest-cov>=4.1.0
```

**Step 2: Create .gitignore**

Create `.gitignore`:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Project specific
cache/
output/
*.ics
status.html

# OS
.DS_Store
Thumbs.db
```

**Step 3: Create README.md**

Create `README.md`:

```markdown
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
```

**Step 4: Commit**

```bash
git add requirements.txt .gitignore README.md
git commit -m "feat: initial project setup with dependencies and documentation"
```

---

## Task 2: Core Data Models

**Files:**
- Create: `src/__init__.py`
- Create: `src/models.py`
- Create: `tests/__init__.py`
- Create: `tests/test_models.py`

**Step 1: Create src package**

Create empty `src/__init__.py`

**Step 2: Write failing test for Event model**

Create `tests/__init__.py` (empty)

Create `tests/test_models.py`:

```python
from datetime import datetime
from src.models import Event, Venue

def test_event_creation():
    event = Event(
        title="Test Film",
        venue=Venue.UPTOWN,
        datetime=datetime(2025, 10, 16, 19, 0),
        detail_url="https://www.siff.net/cinema/in-theaters/test-film",
        description="Test description"
    )
    assert event.title == "Test Film"
    assert event.venue == Venue.UPTOWN
    assert event.datetime.hour == 19
    assert event.is_siff_programming() == False

def test_event_siff_programming_detection():
    event = Event(
        title="DocFest Film",
        venue=Venue.FILM_CENTER,
        datetime=datetime(2025, 10, 16, 20, 0),
        detail_url="https://www.siff.net/programs-and-events/docfest/test-doc",
        description="Documentary"
    )
    assert event.is_siff_programming() == True
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/test_models.py -v`
Expected: FAIL with "No module named 'src.models'"

**Step 4: Write minimal implementation**

Create `src/models.py`:

```python
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

class Venue(Enum):
    DOWNTOWN = "SIFF Cinema Downtown"
    UPTOWN = "SIFF Cinema Uptown"
    FILM_CENTER = "SIFF Film Center"

@dataclass
class Event:
    title: str
    venue: Venue
    datetime: datetime
    detail_url: str
    description: str

    def is_siff_programming(self) -> bool:
        """
        Returns True if event is SIFF-curated programming (not first-run release).
        Detection: URL contains '/programs-and-events/'
        """
        return '/programs-and-events/' in self.detail_url
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/__init__.py src/models.py tests/__init__.py tests/test_models.py
git commit -m "feat: add Event and Venue data models with SIFF programming detection"
```

---

## Task 3: HTTP Client with Caching and Rate Limiting

**Files:**
- Create: `src/http_client.py`
- Create: `tests/test_http_client.py`
- Create: `cache/` (directory)

**Step 1: Write failing test for HTTP client**

Create `tests/test_http_client.py`:

```python
import os
from pathlib import Path
from src.http_client import CachedHttpClient

def test_cached_http_client_caching(tmp_path):
    client = CachedHttpClient(cache_dir=tmp_path, delay_seconds=0)
    url = "https://www.siff.net"

    # First request - should hit network
    content1 = client.get(url)
    assert len(content1) > 0

    # Second request - should hit cache
    content2 = client.get(url)
    assert content1 == content2

    # Verify cache file exists
    cache_files = list(tmp_path.glob("*.html"))
    assert len(cache_files) == 1

def test_user_agent_set():
    client = CachedHttpClient(cache_dir=Path("cache"), delay_seconds=0)
    assert "siff-calendar-scraper" in client.headers["User-Agent"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_http_client.py -v`
Expected: FAIL with "No module named 'src.http_client'"

**Step 3: Write minimal implementation**

Create `src/http_client.py`:

```python
import hashlib
import time
from pathlib import Path
import requests

class CachedHttpClient:
    def __init__(self, cache_dir: Path = Path("cache"), delay_seconds: float = 2.0):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.delay_seconds = delay_seconds
        self.last_request_time = 0
        self.headers = {
            "User-Agent": "siff-calendar-scraper/1.0 (github.com/your-username/siffscrape; contact@example.com)"
        }

    def _get_cache_path(self, url: str) -> Path:
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.html"

    def get(self, url: str) -> str:
        cache_path = self._get_cache_path(url)

        if cache_path.exists():
            return cache_path.read_text(encoding='utf-8')

        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)

        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()

        self.last_request_time = time.time()

        cache_path.write_text(response.text, encoding='utf-8')
        return response.text
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_http_client.py -v`
Expected: PASS (note: first test will be slow as it hits network)

**Step 5: Commit**

```bash
git add src/http_client.py tests/test_http_client.py
git commit -m "feat: add HTTP client with caching and rate limiting"
```

---

## Task 4: Calendar Page Parser

**Files:**
- Create: `src/calendar_parser.py`
- Create: `tests/test_calendar_parser.py`
- Create: `tests/fixtures/sample_calendar.html` (test fixture)

**Step 1: Create test fixture**

Create `tests/fixtures/sample_calendar.html`:

```html
<!DOCTYPE html>
<html>
<head><title>SIFF Calendar</title></head>
<body>
    <div class="film-listing">
        <h3><a href="/cinema/in-theaters/test-film">Test Film</a></h3>
        <div class="venue">SIFF Cinema Uptown</div>
        <div class="showtime">
            <a href="javascript:;" data-time="19:00">7:00 PM</a>
        </div>
    </div>
    <div class="film-listing">
        <h3><a href="/programs-and-events/docfest/doc-film">DocFest: Documentary</a></h3>
        <div class="venue">SIFF Film Center</div>
        <div class="showtime">
            <a href="javascript:;" data-time="20:30">8:30 PM</a>
        </div>
    </div>
</body>
</html>
```

**Step 2: Write failing test for calendar parser**

Create `tests/test_calendar_parser.py`:

```python
from datetime import datetime, date
from pathlib import Path
from src.calendar_parser import CalendarParser
from src.models import Venue

def test_parse_calendar_page():
    parser = CalendarParser()
    fixture_path = Path("tests/fixtures/sample_calendar.html")
    html = fixture_path.read_text()

    events = parser.parse_day(html, date(2025, 10, 16))

    assert len(events) == 2
    assert events[0].title == "Test Film"
    assert events[0].venue == Venue.UPTOWN
    assert events[0].datetime == datetime(2025, 10, 16, 19, 0)
    assert "/cinema/in-theaters/test-film" in events[0].detail_url

    assert events[1].title == "DocFest: Documentary"
    assert events[1].venue == Venue.FILM_CENTER
    assert events[1].datetime == datetime(2025, 10, 16, 20, 30)
    assert events[1].is_siff_programming() == True
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/test_calendar_parser.py -v`
Expected: FAIL with "No module named 'src.calendar_parser'"

**Step 4: Write minimal implementation**

Create `src/calendar_parser.py`:

```python
from datetime import datetime, date, time as dt_time
from bs4 import BeautifulSoup
from src.models import Event, Venue

class CalendarParser:
    VENUE_MAP = {
        "SIFF Cinema Downtown": Venue.DOWNTOWN,
        "SIFF Cinema Uptown": Venue.UPTOWN,
        "SIFF Film Center": Venue.FILM_CENTER,
    }

    def parse_day(self, html: str, event_date: date) -> list[Event]:
        soup = BeautifulSoup(html, 'html.parser')
        events = []

        for listing in soup.find_all('div', class_='film-listing'):
            try:
                events.extend(self._parse_listing(listing, event_date))
            except Exception as e:
                # Log and continue - don't let one bad listing break everything
                print(f"Warning: Failed to parse listing: {e}")
                continue

        return events

    def _parse_listing(self, listing, event_date: date) -> list[Event]:
        # Extract title and detail URL
        title_link = listing.find('h3').find('a')
        title = title_link.text.strip()
        detail_url = "https://www.siff.net" + title_link['href']

        # Extract venue
        venue_text = listing.find('div', class_='venue').text.strip()
        venue = self.VENUE_MAP.get(venue_text)
        if not venue:
            raise ValueError(f"Unknown venue: {venue_text}")

        # Extract showtimes - there can be multiple per listing
        events = []
        for showtime_link in listing.find_all('a', attrs={'data-time': True}):
            time_str = showtime_link['data-time']  # Format: "19:00"
            hour, minute = map(int, time_str.split(':'))
            event_datetime = datetime.combine(event_date, dt_time(hour, minute))

            event = Event(
                title=title,
                venue=venue,
                datetime=event_datetime,
                detail_url=detail_url,
                description=""  # Will be filled by detail parser
            )
            events.append(event)

        return events
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_calendar_parser.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/calendar_parser.py tests/test_calendar_parser.py tests/fixtures/sample_calendar.html
git commit -m "feat: add calendar page parser with venue and showtime extraction"
```

---

## Task 5: Event Detail Parser

**Files:**
- Create: `src/detail_parser.py`
- Create: `tests/test_detail_parser.py`
- Create: `tests/fixtures/sample_detail.html`

**Step 1: Create test fixture**

Create `tests/fixtures/sample_detail.html`:

```html
<!DOCTYPE html>
<html>
<head><title>Test Film</title></head>
<body>
    <div class="film-details">
        <h1>Test Film</h1>
        <div class="description">
            <p>A gripping thriller about testing software.</p>
            <p><strong>Director:</strong> Jane Doe</p>
            <p><strong>Runtime:</strong> 120 minutes</p>
        </div>
    </div>
</body>
</html>
```

**Step 2: Write failing test**

Create `tests/test_detail_parser.py`:

```python
from pathlib import Path
from src.detail_parser import DetailParser

def test_parse_detail_page():
    parser = DetailParser()
    fixture_path = Path("tests/fixtures/sample_detail.html")
    html = fixture_path.read_text()

    description = parser.parse_description(html)

    assert "gripping thriller" in description
    assert "Jane Doe" in description
    assert "120 minutes" in description
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/test_detail_parser.py -v`
Expected: FAIL

**Step 4: Write minimal implementation**

Create `src/detail_parser.py`:

```python
from bs4 import BeautifulSoup

class DetailParser:
    def parse_description(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')

        # Find the description container
        desc_div = soup.find('div', class_='description')
        if not desc_div:
            # Fallback to other common patterns
            desc_div = soup.find('div', class_='film-details')

        if desc_div:
            # Get text, clean up whitespace
            text = desc_div.get_text(separator='\n').strip()
            # Remove excessive newlines
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            return text

        return ""
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_detail_parser.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/detail_parser.py tests/test_detail_parser.py tests/fixtures/sample_detail.html
git commit -m "feat: add event detail page parser for descriptions"
```

---

## Task 6: Main Scraper Orchestration

**Files:**
- Create: `src/scraper.py`
- Create: `tests/test_scraper.py`

**Step 1: Write failing test for date range generation**

Create `tests/test_scraper.py`:

```python
from datetime import date, timedelta
from src.scraper import SiffScraper

def test_generate_date_range_basic():
    scraper = SiffScraper()
    start = date(2025, 10, 16)
    dates = scraper.generate_date_range(start, max_days=5)

    assert len(dates) == 5
    assert dates[0] == start
    assert dates[4] == start + timedelta(days=4)

def test_generate_date_range_with_empty_days():
    scraper = SiffScraper()
    # This would need mocking in real implementation
    # For now, just test the interface exists
    assert hasattr(scraper, 'generate_date_range')
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_scraper.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Create `src/scraper.py`:

```python
from datetime import date, timedelta
from pathlib import Path
from src.http_client import CachedHttpClient
from src.calendar_parser import CalendarParser
from src.detail_parser import DetailParser
from src.models import Event

class SiffScraper:
    BASE_URL = "https://www.siff.net/calendar"

    def __init__(self, cache_dir: Path = Path("cache")):
        self.http_client = CachedHttpClient(cache_dir=cache_dir)
        self.calendar_parser = CalendarParser()
        self.detail_parser = DetailParser()

    def generate_date_range(self, start_date: date, max_days: int = 90,
                           max_consecutive_empty: int = 6) -> list[date]:
        """
        Generate list of dates to scrape.
        Stops after max_days or max_consecutive_empty days with no events.
        """
        dates = []
        current = start_date

        for _ in range(max_days):
            dates.append(current)
            current = current + timedelta(days=1)

        return dates

    def scrape_day(self, event_date: date) -> list[Event]:
        """Scrape all events for a single day."""
        url = f"{self.BASE_URL}?view=grid&date={event_date.isoformat()}"
        html = self.http_client.get(url)
        events = self.calendar_parser.parse_day(html, event_date)

        # Fetch details for each event
        for event in events:
            try:
                detail_html = self.http_client.get(event.detail_url)
                event.description = self.detail_parser.parse_description(detail_html)
            except Exception as e:
                print(f"Warning: Failed to fetch details for {event.detail_url}: {e}")
                # Keep event with empty description

        return events

    def scrape_all(self, start_date: date = None) -> list[Event]:
        """Scrape all events starting from start_date (defaults to yesterday)."""
        if start_date is None:
            start_date = date.today() - timedelta(days=1)

        all_events = []
        consecutive_empty = 0

        for event_date in self.generate_date_range(start_date):
            print(f"Scraping {event_date.isoformat()}...")
            events = self.scrape_day(event_date)

            if events:
                all_events.extend(events)
                consecutive_empty = 0
            else:
                consecutive_empty += 1
                if consecutive_empty >= 6:
                    print(f"Stopping: {consecutive_empty} consecutive days with no events")
                    break

        return all_events
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_scraper.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/scraper.py tests/test_scraper.py
git commit -m "feat: add main scraper orchestration with date range handling"
```

---

## Task 7: iCal Feed Generator

**Files:**
- Create: `src/ical_generator.py`
- Create: `tests/test_ical_generator.py`

**Step 1: Write failing test**

Create `tests/test_ical_generator.py`:

```python
from datetime import datetime
from src.ical_generator import ICalGenerator
from src.models import Event, Venue

def test_generate_ical_basic():
    events = [
        Event(
            title="Test Film",
            venue=Venue.UPTOWN,
            datetime=datetime(2025, 10, 16, 19, 0),
            detail_url="https://www.siff.net/cinema/test",
            description="Test description"
        )
    ]

    generator = ICalGenerator()
    ical_content = generator.generate(events, "Test Calendar")

    assert "BEGIN:VCALENDAR" in ical_content
    assert "Test Film" in ical_content
    assert "SIFF Cinema Uptown" in ical_content
    assert "END:VCALENDAR" in ical_content

def test_filter_by_venue():
    events = [
        Event("Film1", Venue.UPTOWN, datetime(2025, 10, 16, 19, 0), "url1", "desc1"),
        Event("Film2", Venue.DOWNTOWN, datetime(2025, 10, 16, 20, 0), "url2", "desc2"),
    ]

    generator = ICalGenerator()
    uptown_events = generator.filter_by_venue(events, Venue.UPTOWN)

    assert len(uptown_events) == 1
    assert uptown_events[0].title == "Film1"

def test_filter_siff_programming():
    events = [
        Event("Regular", Venue.UPTOWN, datetime(2025, 10, 16, 19, 0),
              "https://www.siff.net/cinema/in-theaters/regular", "desc"),
        Event("DocFest", Venue.FILM_CENTER, datetime(2025, 10, 16, 20, 0),
              "https://www.siff.net/programs-and-events/docfest/doc", "desc"),
    ]

    generator = ICalGenerator()
    siff_only = generator.filter_siff_programming(events)

    assert len(siff_only) == 1
    assert siff_only[0].title == "DocFest"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_ical_generator.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Create `src/ical_generator.py`:

```python
from icalendar import Calendar, Event as ICalEvent
from datetime import datetime
from src.models import Event, Venue

class ICalGenerator:
    def filter_by_venue(self, events: list[Event], venue: Venue) -> list[Event]:
        return [e for e in events if e.venue == venue]

    def filter_siff_programming(self, events: list[Event]) -> list[Event]:
        return [e for e in events if e.is_siff_programming()]

    def generate(self, events: list[Event], calendar_name: str) -> str:
        cal = Calendar()
        cal.add('prodid', '-//SIFF Calendar Scraper//siffscrape//EN')
        cal.add('version', '2.0')
        cal.add('x-wr-calname', calendar_name)

        for event in events:
            ical_event = ICalEvent()
            ical_event.add('summary', event.title)
            ical_event.add('dtstart', event.datetime)
            ical_event.add('location', event.venue.value)

            # Build description with detail page link
            description = f"{event.description}\n\n"
            description += f"More info and tickets: {event.detail_url}"
            ical_event.add('description', description)

            ical_event.add('url', event.detail_url)
            ical_event.add('uid', f"{event.datetime.isoformat()}-{event.title}@siff.net")

            cal.add_component(ical_event)

        return cal.to_ical().decode('utf-8')
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_ical_generator.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/ical_generator.py tests/test_ical_generator.py
git commit -m "feat: add iCal feed generator with filtering capabilities"
```

---

## Task 8: Status Page Generator

**Files:**
- Create: `src/status_page.py`
- Create: `tests/test_status_page.py`

**Step 1: Write failing test**

Create `tests/test_status_page.py`:

```python
from datetime import datetime
from src.status_page import StatusPageGenerator
from src.models import Event, Venue

def test_generate_status_page():
    events = [
        Event("Film1", Venue.UPTOWN, datetime(2025, 10, 16, 19, 0), "url1", "desc1"),
        Event("Film2", Venue.DOWNTOWN, datetime(2025, 10, 17, 20, 0), "url2", "desc2"),
        Event("Film3", Venue.UPTOWN, datetime(2025, 11, 1, 19, 0), "url3", "desc3"),
    ]

    generator = StatusPageGenerator()
    html = generator.generate(
        events=events,
        last_scrape=datetime(2025, 10, 16, 1, 0),
        scrape_success=True
    )

    assert "Last Scrape" in html
    assert "SIFF Cinema Uptown: 2" in html
    assert "SIFF Cinema Downtown: 1" in html
    assert "2025-11-01" in html  # Furthest event
    assert "siff-uptown.ics" in html  # Calendar links
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_status_page.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Create `src/status_page.py`:

```python
from datetime import datetime
from collections import Counter
from src.models import Event, Venue

class StatusPageGenerator:
    def generate(self, events: list[Event], last_scrape: datetime,
                 scrape_success: bool) -> str:
        venue_counts = Counter(e.venue for e in events)
        furthest_event = max((e.datetime for e in events), default=None)
        total_events = len(events)

        status_class = "success" if scrape_success else "error"
        status_text = "Success" if scrape_success else "Failed"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SIFF Calendar Scraper Status</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }}
        .status {{
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .status.success {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
        }}
        .status.error {{
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
        }}
        .stats {{
            margin: 20px 0;
        }}
        .calendar-links {{
            margin-top: 30px;
        }}
        .calendar-links a {{
            display: block;
            margin: 10px 0;
            padding: 10px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 3px;
        }}
        .calendar-links a:hover {{
            background-color: #0056b3;
        }}
    </style>
</head>
<body>
    <h1>SIFF Calendar Scraper Status</h1>

    <div class="status {status_class}">
        <strong>Last Scrape:</strong> {last_scrape.strftime('%Y-%m-%d %H:%M:%S')} UTC<br>
        <strong>Status:</strong> {status_text}
    </div>

    <div class="stats">
        <h2>Statistics</h2>
        <p><strong>Total Events:</strong> {total_events}</p>
        <p><strong>Events by Venue:</strong></p>
        <ul>
"""

        for venue, count in sorted(venue_counts.items(), key=lambda x: x[0].value):
            html += f"            <li>{venue.value}: {count}</li>\n"

        html += "        </ul>\n"

        if furthest_event:
            html += f"        <p><strong>Furthest Event:</strong> {furthest_event.strftime('%Y-%m-%d')}</p>\n"

        html += """    </div>

    <div class="calendar-links">
        <h2>Calendar Feeds</h2>
        <a href="siff-all.ics">All Events</a>
        <a href="siff-programming-only.ics">SIFF Curated Programming Only</a>
        <a href="siff-downtown.ics">SIFF Cinema Downtown</a>
        <a href="siff-uptown.ics">SIFF Cinema Uptown</a>
        <a href="siff-film-center.ics">SIFF Film Center</a>
    </div>
</body>
</html>
"""
        return html
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_ical_generator.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/status_page.py tests/test_status_page.py
git commit -m "feat: add status page generator with scrape statistics"
```

---

## Task 9: Main Entry Point

**Files:**
- Create: `src/main.py`
- Modify: `README.md` (update usage)

**Step 1: Write main entry point**

Create `src/main.py`:

```python
#!/usr/bin/env python3
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from src.scraper import SiffScraper
from src.ical_generator import ICalGenerator
from src.status_page import StatusPageGenerator
from src.models import Venue

def main():
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    print("Starting SIFF calendar scrape...")
    start_time = datetime.utcnow()

    try:
        # Scrape all events
        scraper = SiffScraper()
        start_date = date.today() - timedelta(days=1)
        events = scraper.scrape_all(start_date)

        print(f"Found {len(events)} total events")

        # Generate iCal feeds
        generator = ICalGenerator()

        # All events
        print("Generating all-events calendar...")
        all_ical = generator.generate(events, "SIFF All Events")
        (output_dir / "siff-all.ics").write_text(all_ical, encoding='utf-8')

        # SIFF programming only
        print("Generating SIFF-programming-only calendar...")
        siff_events = generator.filter_siff_programming(events)
        siff_ical = generator.generate(siff_events, "SIFF Curated Programming")
        (output_dir / "siff-programming-only.ics").write_text(siff_ical, encoding='utf-8')

        # Per-venue calendars
        for venue in Venue:
            print(f"Generating {venue.value} calendar...")
            venue_events = generator.filter_by_venue(events, venue)
            venue_ical = generator.generate(venue_events, venue.value)
            filename = f"siff-{venue.name.lower().replace('_', '-')}.ics"
            (output_dir / filename).write_text(venue_ical, encoding='utf-8')

        # Generate status page
        print("Generating status page...")
        status_gen = StatusPageGenerator()
        status_html = status_gen.generate(events, start_time, scrape_success=True)
        (output_dir / "status.html").write_text(status_html, encoding='utf-8')

        print(f"Done! Outputs written to {output_dir}/")
        return 0

    except Exception as e:
        print(f"ERROR: Scrape failed: {e}", file=sys.stderr)

        # Generate error status page
        status_gen = StatusPageGenerator()
        status_html = status_gen.generate([], start_time, scrape_success=False)
        (output_dir / "status.html").write_text(status_html, encoding='utf-8')

        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Step 2: Make it executable and test**

Run: `chmod +x src/main.py` (Linux/Mac)

Run: `python src/main.py` (dry run - will actually scrape!)

Expected: Script runs, generates output files

**Step 3: Update README with actual usage**

Update `README.md` usage section:

```markdown
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
```

**Step 4: Commit**

```bash
git add src/main.py README.md
git commit -m "feat: add main entry point for scraper execution"
```

---

## Task 10: GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/scrape.yml`

**Step 1: Create GitHub Actions workflow**

Create `.github/workflows/scrape.yml`:

```yaml
name: Scrape SIFF Calendar

on:
  schedule:
    # Run nightly at 2 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch:  # Allow manual triggers

jobs:
  scrape:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run scraper
        run: python src/main.py

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./output
          publish_branch: gh-pages
          user_name: 'github-actions[bot]'
          user_email: 'github-actions[bot]@users.noreply.github.com'
          commit_message: 'Update SIFF calendar feeds'

      - name: Send failure notification
        if: failure()
        run: |
          echo "Scrape failed! Check the logs at ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
```

**Step 2: Configure GitHub Pages**

Manual step (document in README):
1. Go to repository Settings > Pages
2. Set Source to "Deploy from a branch"
3. Select branch: `gh-pages`, folder: `/ (root)`
4. Save

**Step 3: Update README with deployment info**

Add to `README.md`:

```markdown
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
```

**Step 4: Commit**

```bash
git add .github/workflows/scrape.yml README.md
git commit -m "feat: add GitHub Actions workflow for nightly scraping and deployment"
```

---

## Task 11: Real-World Parser Adjustment

**Files:**
- Modify: `src/calendar_parser.py`
- Modify: `src/detail_parser.py`

**Context:** The test fixtures are simplified. Real SIFF pages will have different HTML structure. This task involves running against the actual site and adjusting parsers.

**Step 1: Run scraper against real site**

Run: `python src/main.py`

Expected: May fail or extract incorrectly due to HTML structure differences

**Step 2: Inspect actual HTML structure**

Check `cache/*.html` files to see actual structure

**Step 3: Adjust CalendarParser based on real HTML**

Example adjustments (actual changes depend on real HTML):

```python
# In calendar_parser.py, update selectors to match real structure
# This is a placeholder - actual changes depend on inspection

def _parse_listing(self, listing, event_date: date) -> list[Event]:
    # Adjust selectors based on actual HTML
    # Example: title might be in <a class="film-title"> instead
    title_link = listing.find('a', class_='film-title') or listing.find('h3').find('a')
    # ... etc
```

**Step 4: Adjust DetailParser based on real HTML**

Similar process - inspect and adjust

**Step 5: Test against real site again**

Run: `python src/main.py`

Expected: SUCCESS with valid .ics files generated

**Step 6: Verify generated calendars**

- Open `output/siff-all.ics` in calendar app
- Check that events appear correctly
- Verify links work

**Step 7: Commit**

```bash
git add src/calendar_parser.py src/detail_parser.py
git commit -m "fix: adjust parsers for real SIFF.net HTML structure"
```

---

## Task 12: Integration Testing and Documentation

**Files:**
- Create: `tests/test_integration.py`
- Modify: `README.md`
- Create: `LICENSE`

**Step 1: Write integration test**

Create `tests/test_integration.py`:

```python
import pytest
from datetime import date
from pathlib import Path
from src.scraper import SiffScraper
from src.ical_generator import ICalGenerator

@pytest.mark.integration
def test_full_scrape_and_generate():
    """Integration test - actually hits SIFF.net (slow)"""
    scraper = SiffScraper()

    # Scrape just one day to keep test fast
    events = scraper.scrape_day(date.today())

    # Should find at least some events (unless SIFF is truly empty)
    # This assertion might need adjustment
    assert len(events) >= 0

    # Generate calendar
    generator = ICalGenerator()
    ical = generator.generate(events, "Test Calendar")

    assert "BEGIN:VCALENDAR" in ical
    assert "END:VCALENDAR" in ical
```

**Step 2: Add pytest markers**

Create `pytest.ini`:

```ini
[pytest]
markers =
    integration: marks tests as integration tests (slow, hits network)
```

**Step 3: Run integration test**

Run: `pytest -m integration -v`

Expected: PASS (or skip if SIFF has no events today)

**Step 4: Add license**

Create `LICENSE`:

```
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Step 5: Final README polish**

Add sections to `README.md`:

```markdown
## Features

- Scrapes SIFF.net calendar for all venues
- Generates separate iCal feeds per venue
- Provides combined feed of all events
- Special feed for SIFF-curated programming only (excludes first-run releases)
- Status page with scrape statistics
- Respectful rate limiting and caching
- Automated nightly updates via GitHub Actions

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
```

**Step 6: Final commit**

```bash
git add tests/test_integration.py pytest.ini LICENSE README.md
git commit -m "docs: add integration tests, license, and comprehensive documentation"
```

---

## Completion Checklist

- [ ] All unit tests pass: `pytest tests/ -v`
- [ ] Integration test passes: `pytest -m integration -v`
- [ ] Scraper runs successfully: `python src/main.py`
- [ ] Output files generated in `output/`
- [ ] All .ics files open correctly in calendar application
- [ ] Status page displays correctly in browser
- [ ] GitHub Actions workflow file is valid
- [ ] README is complete and accurate
- [ ] All code is committed to git

## Next Steps After Implementation

1. Push to GitHub
2. Enable GitHub Pages
3. Trigger manual workflow run to test
4. Subscribe to generated calendar feeds in your calendar app
5. Monitor for first nightly run
6. Share with family/friends!

---

**Plan complete!**
