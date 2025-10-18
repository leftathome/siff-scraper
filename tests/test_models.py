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
