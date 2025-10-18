import os
from pathlib import Path
from src.http_client import CachedHttpClient

def test_cached_http_client_caching(tmp_path):
    client = CachedHttpClient(cache_dir=tmp_path, delay_seconds=0)
    url = "https://www.siff.net"

    # First request - should hit network
    content1 = client.get(url)
    assert len(content1) > 0

    # Second request - should hit cache
    content2 = client.get(url)
    assert content1 == content2

    # Verify cache file exists
    cache_files = list(tmp_path.glob("*.html"))
    assert len(cache_files) == 1

def test_user_agent_set():
    client = CachedHttpClient(cache_dir=Path("cache"), delay_seconds=0)
    assert "siff-calendar-scraper" in client.headers["User-Agent"]
