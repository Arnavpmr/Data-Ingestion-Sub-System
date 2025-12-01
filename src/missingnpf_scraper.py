import requests
import os
import time
from datetime import datetime
from bs4 import BeautifulSoup

BASE_URL = "https://missingnpf.com/"
OUTPUT_BASE_DIR = "data/raw/missingnpf"
DELAY = 1.0
LIMIT = 10
START_PAGE = 1

# Create a folder for this run using current date
today = datetime.now().strftime("%Y-%m-%d")
RUN_DIR = os.path.join(OUTPUT_BASE_DIR, today)
os.makedirs(RUN_DIR, exist_ok=True)

def url_params(page):
    return {
        "vx": 1,
        "action": "search_posts",
        "type": "people",
        "sort": "alphabetical",
        "pg": page,
        "limit": LIMIT,
        "__template_id": 9088,
        "__get_total_count": 1
    }

def fetch_page(page):
    r = requests.get(BASE_URL, params=url_params(page), timeout=15)
    r.raise_for_status()
    return r.text

def save_page(page, html):
    path = os.path.join(RUN_DIR, f"missing_{page}.html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print("Saved:", path)

def has_results(html):
    """Check if page has any results"""
    soup = BeautifulSoup(html, "html.parser")
    info_tag = soup.find("script", class_="info")

    if info_tag: return info_tag.get("data-has-results", "false").lower() == "true"

    return False

def scrape_all(start_page=START_PAGE, delay=DELAY):
    page = start_page

    while True:
        print("Fetching page", page)
        html = fetch_page(page)

        if not has_results(html):
            print("Empty response — stopping job.")
            break

        save_page(page, html)
        page += 1
        time.sleep(delay)
    
    print(f"Fetched {page} pages!")

if __name__ == "__main__":
    scrape_all()