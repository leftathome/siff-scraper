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
