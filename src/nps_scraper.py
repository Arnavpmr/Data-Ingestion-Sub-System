import requests
import os
import time
from datetime import datetime
from bs4 import BeautifulSoup

BASE_URL = "https://www.nps.gov/orgs/1563/cold-cases.htm"
OUTPUT_BASE_DIR = "data/raw/nps"

# Create a folder for this run using current date
today = datetime.now().strftime("%Y-%m-%d")
RUN_DIR = os.path.join(OUTPUT_BASE_DIR, today)
os.makedirs(RUN_DIR, exist_ok=True)

def fetch_all():
    r = requests.get(BASE_URL, timeout=15)
    r.raise_for_status()
    return r.text

def save_page(html):
    path = os.path.join(RUN_DIR, "nps_cold_cases.html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print("Saved:", path)

if __name__ == "__main__":
    html = fetch_all()
    save_page(html)