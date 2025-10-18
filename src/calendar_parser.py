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
