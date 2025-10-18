from bs4 import BeautifulSoup

class DetailParser:
    def parse_description(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')

        desc_div = soup.find('div', class_='description')
        if not desc_div:
            desc_div = soup.find('div', class_='film-details')

        if desc_div:
            text = desc_div.get_text(separator='\n').strip()
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            return text

        return ""
