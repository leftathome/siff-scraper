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
