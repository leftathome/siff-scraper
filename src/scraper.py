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
