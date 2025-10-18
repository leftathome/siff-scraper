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
    assert "2025-11-01" in html
    assert "siff-uptown.ics" in html
