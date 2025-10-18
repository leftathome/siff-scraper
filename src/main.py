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
        (output_dir / "index.html").write_text(status_html, encoding='utf-8')

        print(f"Done! Outputs written to {output_dir}/")
        return 0

    except Exception as e:
        print(f"ERROR: Scrape failed: {e}", file=sys.stderr)

        # Generate error status page
        status_gen = StatusPageGenerator()
        status_html = status_gen.generate([], start_time, scrape_success=False)
        (output_dir / "index.html").write_text(status_html, encoding='utf-8')

        return 1

if __name__ == "__main__":
    sys.exit(main())
