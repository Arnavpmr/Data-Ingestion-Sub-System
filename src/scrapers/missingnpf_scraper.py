import requests
import os
import time
import re

from datetime import datetime
from bs4 import BeautifulSoup

from log_config import get_logger

BASE_URL = "https://missingnpf.com/"
OUTPUT_BASE_DIR = "data/raw/missingnpf"
DELAY = 1.0
PEOPLE_PER_PAGE = 10
START_PAGE = 1

today = datetime.now().strftime("%Y-%m-%d")
RUN_DIR = os.path.join(OUTPUT_BASE_DIR, today)
PAGES_DIR = os.path.join(RUN_DIR, "pages")

logger = get_logger(module_name=__name__)

def url_params(page):
    return {
        "vx": 1,
        "action": "search_posts",
        "type": "people",
        "sort": "alphabetical",
        "pg": page,
        "limit": PEOPLE_PER_PAGE,
        "__template_id": 9088,
        "__get_total_count": 1
    }

def fetch_page(page):
    try:
        r = requests.get(BASE_URL, params=url_params(page), timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        logger.error(f"Error fetching page {page}: {e}")

def save_profile(name, html):
    path = os.path.join(RUN_DIR, f"{name}.html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    logger.debug(f"Saved Profile: {name}")

def has_results(html):
    """Check if page has any results"""
    soup = BeautifulSoup(html, "lxml")
    info_tag = soup.find("script", class_="info")

    if info_tag: return info_tag.get("data-has-results", "false").lower() == "true"

    return False

def name_to_url(name):
    # lowercase all characters, remove parentheses, and replace spaces with hyphens
    name = re.sub(r'[()]', '', name)
    return name.lower().strip().replace(' ', '-')

def scrape_all_profiles(start_page=START_PAGE, delay=DELAY):
    os.makedirs(RUN_DIR, exist_ok=True)
    os.makedirs(PAGES_DIR, exist_ok=True)

    page_count = start_page
    logger = get_logger(module_name=__name__)

    while True:
        logger.debug(f"Fetching page {page_count}")
        html = fetch_page(page_count)

        if not has_results(html):
            logger.debug("Empty response — stopping job.")
            break

        # save page html for reference
        with open(os.path.join(PAGES_DIR, f"page_{page_count}.html"), 
                  "w", encoding="utf-8") as f:
            f.write(html)
            
        # get all names from profile page
        soup = BeautifulSoup(html, 'lxml')
        previews = soup.find_all('div', class_='ts-preview')
        for preview in previews:
            heading = preview.find('h3', class_='elementor-heading-title')

            if heading and heading.find('a'):
                full_name = heading.find('a').text.strip()
                logger.debug(f"Fetching profile for {full_name}")

                try:
                    r = requests.get(BASE_URL + "people/" + name_to_url(full_name))
                    r.raise_for_status()
                    save_profile(name_to_url(full_name), r.text)
                except Exception as e:
                    logger.error(f"Failed to fetch profile for {full_name}: {e}")

                time.sleep(delay)

        page_count += 1
        time.sleep(delay)
    
    logger.info(f"Scraped {page_count} pages!")