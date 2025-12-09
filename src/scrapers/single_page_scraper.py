import requests
import os
from datetime import datetime

class SinglePageScraper:
    def __init__(self, name, base_url):
        self.name = name
        self.base_url = base_url

    def fetch_page(self):
        r = requests.get(self.base_url, timeout=15)
        r.raise_for_status()
        return r.text

    def save_page(self, html):
        today = datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(f'data/raw/{self.name}/{today}', self.name + ".html")

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)