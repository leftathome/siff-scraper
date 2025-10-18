from datetime import datetime
from collections import Counter
from src.models import Event, Venue

class StatusPageGenerator:
    def generate(self, events: list[Event], last_scrape: datetime,
                 scrape_success: bool) -> str:
        venue_counts = Counter(e.venue for e in events)
        furthest_event = max((e.datetime for e in events), default=None)
        total_events = len(events)

        status_class = "success" if scrape_success else "error"
        status_text = "Success" if scrape_success else "Failed"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SIFF Calendar Scraper Status</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }}
        .status {{
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .status.success {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
        }}
        .status.error {{
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
        }}
        .stats {{
            margin: 20px 0;
        }}
        .calendar-links {{
            margin-top: 30px;
        }}
        .calendar-links a {{
            display: block;
            margin: 10px 0;
            padding: 10px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 3px;
        }}
        .calendar-links a:hover {{
            background-color: #0056b3;
        }}
        .disclaimer {{
            padding: 15px;
            margin-bottom: 20px;
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 5px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>SIFF Calendar Scraper Status</h1>

    <div class="disclaimer">
        <strong>Disclaimer:</strong> This is an independent, unofficial project and is not affiliated with, endorsed by, or connected to the Seattle International Film Festival (SIFF) or SIFF.net in any way. All event data is sourced from the public SIFF.net website.
    </div>

    <div class="status {status_class}">
        <strong>Last Scrape:</strong> {last_scrape.strftime('%Y-%m-%d %H:%M:%S')} UTC<br>
        <strong>Status:</strong> {status_text}
    </div>

    <div class="stats">
        <h2>Statistics</h2>
        <p><strong>Total Events:</strong> {total_events}</p>
        <p><strong>Events by Venue:</strong></p>
        <ul>
"""

        for venue, count in sorted(venue_counts.items(), key=lambda x: x[0].value):
            html += f"            <li>{venue.value}: {count}</li>\n"

        html += "        </ul>\n"

        if furthest_event:
            html += f"        <p><strong>Furthest Event:</strong> {furthest_event.strftime('%Y-%m-%d')}</p>\n"

        html += """    </div>

    <div class="calendar-links">
        <h2>Calendar Feeds</h2>
        <a href="siff-all.ics">All Events</a>
        <a href="siff-programming-only.ics">SIFF Curated Programming Only</a>
        <a href="siff-downtown.ics">SIFF Cinema Downtown</a>
        <a href="siff-uptown.ics">SIFF Cinema Uptown</a>
        <a href="siff-film-center.ics">SIFF Film Center</a>
    </div>
</body>
</html>
"""
        return html
