import os

import pandas as pd
from bs4 import BeautifulSoup
import re

from datetime import datetime

from parsers.parser import Parser

from log_config import get_logger

class MissingNPFParser(Parser):
    logger = get_logger(module_name=__name__)

    def __init__(self):
        super().__init__("missingnpf")
    
    def parse(self):
        records = []

        for file in os.listdir(self.input_dir + '/pages'):
            with open(os.path.join(self.input_dir, 'pages', file), 'r', encoding='utf-8') as f:
                MissingNPFParser.logger.debug(f"Parsing file: {file}")
                html_names = f.read()
                soup = BeautifulSoup(html_names, 'lxml')
                previews = soup.find_all('div', class_='ts-preview')

                for preview in previews:
                    full_name = None
                    record = {}

                    # Method 1: Extract name from heading link
                    heading = preview.find('h3', class_='elementor-heading-title')
                    if heading and heading.find('a'):
                        full_name = heading.find('a').text.strip()

                        if not MissingNPFParser._is_valid_name(full_name):
                            MissingNPFParser.logger.debug(f"Rejected: Dropping entry due to invalid name: {full_name}")
                            continue

                        record['name'] = full_name
                            
                    # Extract date missing
                    missing_span = preview.find('span', attrs={'data-text': lambda x: x and 'Reported Missing:' in str(x)})

                    if missing_span:
                        date_text = missing_span.text.strip()
                        date_match = re.search(r'Reported Missing:\s*(.+?)(?:\s*\(|$)', date_text)

                        if date_match:
                            parsed_date = date_match.group(1).strip()
                            years_ago_match = re.search(r'(\d+)\s+years?\s+ago', date_text)

                            if years_ago_match.group(1):
                                years_ago = int(years_ago_match.group(1))
                                current_year = datetime.now().year
                                missing_year = current_year - years_ago
                                record['date_missing'] = parsed_date[:-2] + str(missing_year // 100) + parsed_date[-2:]
                    
                    # Extract last seen location
                    location_span = preview.select_one('ul.premium-bullet-list-box li a span')
                    if location_span:
                        record['last_seen'] = location_span.text.strip()
                    
                    # check if name was found in profiles folder
                    profile_filename = MissingNPFParser._name_to_url(full_name) + '.html'
                    profile_path = os.path.join(self.input_dir, 'profiles', profile_filename)

                    if os.path.exists(profile_path):
                        with open(profile_path, 'r', encoding='utf-8') as pf:
                            profile_html = pf.read()
                            profile_soup = BeautifulSoup(profile_html, 'lxml')

                            demographics_lists = profile_soup.find_all('ul', class_='elementor-icon-list-items')
                            for ul in demographics_lists:
                                list_items = ul.find_all('li', class_='elementor-icon-list-item')
                                for item in list_items:
                                    text = item.get_text(strip=True)
                                    
                                    # Extract age
                                    if 'Age:' in text:
                                        age_match = re.search(r'Age:\s*(\d+)', text)
                                        if age_match and int(age_match.group(1)) > 0:
                                            record['age'] = age_match.group(1)
                                    
                                    # Extract gender
                                    if 'Gender/Sex:' in text:
                                        gender_match = re.search(r'Gender/Sex:\s*(\w+)', text)
                                        if gender_match:
                                            record['gender'] = 'M' if gender_match.group(1)[0] == 'M' else 'F'

                    MissingNPFParser.logger.debug(f"Parsed record: {record}")
                    records.append(record)

        self.df = pd.DataFrame(records)

    @staticmethod
    def _is_valid_name(name):
        blacklist = [
                "Unnamed", "Unidentified", "Unknown", "Remains", "Hiker", "Toddler",
                "River", "Female", "Male", "Overdue", "Marines", "Body", "Skeletal", 
                "Victim", "John Doe", "Jane Doe", "Infant", "Baby", "Child"
            ]
        
        if not (2 <= len(name.split()) <= 4):
            return False

        for word in blacklist:
            pattern = r'John.*Doe|Jane.*Doe'
            if word.lower() in name.lower() or re.search(pattern, name, re.IGNORECASE):
                return False
        
        return True

    @staticmethod
    def _name_to_url(name):
        # lowercase all characters, remove parentheses, and replace spaces with hyphens
        MissingNPFParser.logger.debug(f"Converting name to URL format: {name}")
        name = re.sub(r'[()]', '', name)
        return name.lower().strip().replace(' ', '-')

if __name__ == "__main__":
    parser = MissingNPFParser()

    parser.parse()
    parser.save_csv()