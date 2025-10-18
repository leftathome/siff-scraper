from datetime import datetime, date, time as dt_time
import re
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

        for event_div in soup.find_all('div', class_='event'):
            try:
                event = self._parse_event(event_div, event_date, soup)
                if event:
                    events.append(event)
            except Exception as e:
                print(f"Warning: Failed to parse event: {e}")
                continue

        return events

    def _parse_event(self, event_div, event_date: date, soup) -> Event:
        link = event_div.find('a', class_='open-popup-with-screenings')
        if not link:
            return None

        title_span = link.find('span', class_='title')
        if not title_span:
            return None
        title = title_span.text.strip()

        time_span = link.find('span', class_='time')
        if not time_span:
            return None
        time_text = time_span.text.strip()

        event_datetime = self._parse_time(time_text, event_date)
        if not event_datetime:
            return None

        venue = self._extract_venue_from_classes(event_div.get('class', []))
        if not venue:
            return None

        modal_id = link.get('href', '').lstrip('#')
        detail_url = self._extract_detail_url(soup, modal_id)

        description = self._extract_description(soup, modal_id)

        return Event(
            title=title,
            venue=venue,
            datetime=event_datetime,
            detail_url=detail_url,
            description=description
        )

    def _parse_time(self, time_text: str, event_date: date) -> datetime:
        match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)', time_text, re.IGNORECASE)
        if not match:
            return None

        hour = int(match.group(1))
        minute = int(match.group(2))
        am_pm = match.group(3).lower()

        if am_pm == 'pm' and hour != 12:
            hour += 12
        elif am_pm == 'am' and hour == 12:
            hour = 0

        return datetime.combine(event_date, dt_time(hour, minute))

    def _extract_venue_from_classes(self, classes: list) -> Venue:
        class_str = ' '.join(classes)

        for venue_name, venue_enum in self.VENUE_MAP.items():
            if venue_name in class_str:
                return venue_enum

        return None

    def _extract_detail_url(self, soup, modal_id: str) -> str:
        if not modal_id:
            return ""

        modal = soup.find('div', id=modal_id)
        if not modal:
            return ""

        detail_link = modal.find('a', href=True)
        if detail_link and detail_link.get('href', '').startswith('/'):
            return "https://www.siff.net" + detail_link['href']

        return ""

    def _extract_description(self, soup, modal_id: str) -> str:
        if not modal_id:
            return ""

        modal = soup.find('div', id=modal_id)
        if not modal:
            return ""

        for p in modal.find_all('p'):
            text = p.get_text(strip=True)
            if text and len(text) > 50 and not text.startswith('Saturday') and not text.startswith('Sunday') and not text.startswith('Monday') and not text.startswith('Tuesday') and not text.startswith('Wednesday') and not text.startswith('Thursday') and not text.startswith('Friday'):
                return text

        return ""
