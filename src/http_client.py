import hashlib
import time
from pathlib import Path
import requests

class CachedHttpClient:
    def __init__(self, cache_dir: Path = Path("cache"), delay_seconds: float = 2.0):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.delay_seconds = delay_seconds
        self.last_request_time = 0
        self.headers = {
            "User-Agent": "siff-calendar-scraper/1.0 (github.com/leftathome/siffscrape; leftathome@gmail.com)"
        }

    def _get_cache_path(self, url: str) -> Path:
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.html"

    def get(self, url: str) -> str:
        cache_path = self._get_cache_path(url)

        if cache_path.exists():
            with open(cache_path, 'r', encoding='utf-8', newline='') as f:
                return f.read()

        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)

        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()

        self.last_request_time = time.time()

        with open(cache_path, 'w', encoding='utf-8', newline='') as f:
            f.write(response.text)
        return response.text
