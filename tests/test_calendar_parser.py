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
