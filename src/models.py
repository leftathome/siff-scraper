from datetime import datetime
from enum import Enum
from dataclasses import dataclass

class Venue(Enum):
    DOWNTOWN = "SIFF Cinema Downtown"
    UPTOWN = "SIFF Cinema Uptown"
    FILM_CENTER = "SIFF Film Center"

@dataclass
class Event:
    title: str
    venue: Venue
    datetime: datetime
    detail_url: str
    description: str

    def is_siff_programming(self) -> bool:
        """
        Returns True if event is SIFF-curated programming (not first-run release).
        Detection: URL contains '/programs-and-events/'
        """
        return '/programs-and-events/' in self.detail_url
