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
