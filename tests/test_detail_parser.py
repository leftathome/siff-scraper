from pathlib import Path
from src.detail_parser import DetailParser

def test_parse_detail_page():
    parser = DetailParser()
    fixture_path = Path("tests/fixtures/sample_detail.html")
    html = fixture_path.read_text()

    description = parser.parse_description(html)

    assert "gripping thriller" in description
    assert "Jane Doe" in description
    assert "120 minutes" in description
