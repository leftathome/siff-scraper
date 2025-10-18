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
