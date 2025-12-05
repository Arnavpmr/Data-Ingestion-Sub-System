# Reads the files in the latest folder date from nissingnpf scraper and parses missing persons data
import os

import pandas as pd
from bs4 import BeautifulSoup

from datetime import datetime
from pathlib import Path

import re

today = datetime.now().strftime("%Y-%m-%d")
OUTPUT_BASE_DIR = "data/silver/missingnpf"
RUN_DIR = os.path.join(OUTPUT_BASE_DIR, today)

def get_latest_dir(base_dir="data/raw/missingnpf"):
    date_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

    if not date_dirs:
        raise FileNotFoundError("No valid date directories found in raw missingnpf data.")

    latest_date = max(date_dirs)

    return os.path.join(base_dir, latest_date)

def is_valid_name(name):
    blacklist = [
            "Unnamed", "Unidentified", "Unknown", "Remains", "Hiker", "Toddler",
            "River", "Female", "Male", "Overdue", "Marines", "Body", "Skeletal", "Victim", "John Doe"
        ]
    
    if not (2 <= len(name.split()) <= 4):
        return False

    for word in blacklist:
        if word.lower() in name.lower():
            return False
    
    return True

def name_to_url(name):
    # lowercase all characters, remove parentheses, and replace spaces with hyphens
    name = re.sub(r'[()]', '', name)
    return name.lower().strip().replace(' ', '-')

def parse_missingnpf():
    """Parse the missing persons data from the missingnpf HTML files."""
    latest_dir = get_latest_dir()
    records = []

    for file in os.listdir(latest_dir):
        if file.endswith('.html'):
            with open(os.path.join(latest_dir, file), 'r', encoding='utf-8') as f:
                record = {}
                html_content = f.read()
                soup = BeautifulSoup(html_content, 'lxml')

                #Extract the name
                heading = soup.find('h2', class_='e-link-in-bio__heading')
                if heading and is_valid_name(heading.text.strip()):
                    record['name'] = heading.text.strip()
                else:
                    # Log dropped entries due to invalid names
                    print(f"Dropping entry due to invalid name in file: {file}")
                    continue

                #Extract Demographics
                demographics_lists = soup.find_all('ul', class_='elementor-icon-list-items')
                for ul in demographics_lists:
                    list_items = ul.find_all('li', class_='elementor-icon-list-item')
                    for item in list_items:
                        text = item.get_text(strip=True)
                        
                        # Extract age
                        if 'Age:' in text:
                            age_match = re.search(r'Age:\s*(\d+)', text)
                            if age_match:
                                record['age'] = age_match.group(1)
                        
                        # Extract gender
                        if 'Gender/Sex:' in text:
                            gender_match = re.search(r'Gender/Sex:\s*(\w+)', text)
                            if gender_match:
                                record['gender'] = 'M' if gender_match.group(1)[0] == 'M' else 'F'

                # Extract date missing
                date_spans = soup.find_all('span', attrs={'data-text': True})
                for span in date_spans:
                    data_text = span.get('data-text', '')
                    
                    if 'Reported Missing:' in data_text:
                        date_missing_match = re.search(r'Reported Missing:\s*(.+?)(?:\s*\(|$)', data_text)
                        if date_missing_match:
                            record['date_missing'] = date_missing_match.group(1).strip()
                
                #Extract last seen location
                location_span = soup.find('span', attrs={'data-text': lambda x: x and ('National Forest' in str(x) or 'National Park' in str(x))})
                if location_span:
                    record['last_seen'] = location_span.text.strip()
                
                records.append(record)
            
    df = pd.DataFrame(records)

    os.makedirs(RUN_DIR, exist_ok=True)
    df.to_csv(os.path.join(RUN_DIR, 'missingnpf_data.csv'), index=False)

                
if __name__ == "__main__":
    parse_missingnpf()