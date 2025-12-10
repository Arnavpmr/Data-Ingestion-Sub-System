import difflib
from dateutil import parser as date_parser
import re

import pandas as pd
from bs4 import BeautifulSoup

from parsers.parser import Parser

from log_config import get_logger

# Add some debug logs in this file!

class NPSParser(Parser):
    logger = get_logger(module_name=__name__)

    def __init__(self):
        super().__init__("nps")

    def parse(self):
        with open(f'{self.input_dir}/{self.name}.html', "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "lxml")

            records = []
            cases = soup.find_all('div', class_='Component ArticleTextGroup TextWrapped clearfix')

            for elem in cases:
                record = {}
                text = elem.get_text()

                name_match = re.search(r'Name:\s*([^\n]+)', text)
                if name_match:
                    record['name'] = name_match.group(1).strip()
                    # Remove extra formatting
                    record['name'] = re.sub(r'\s+', ' ', record['name'])

                    NPSParser.logger.debug(f"Extracted name: {record['name']}")
                
                desc_match = re.search(r'Description:\s*([^\n]+(?:\n[^\n]+)*?)(?=Case Info|$)',
                                    text, re.DOTALL)
                if desc_match:
                    description = desc_match.group(1).strip()

                    # Extract Age
                    age_match = re.search(r'(\d+)\s*years?\s*old', description)
                    if age_match:
                        record['age'] = age_match.group(1)
                    
                    # Extract Gender
                    record['gender'] = 'F' if 'female' in description.lower() else 'M'
                
                # Extract Date Missing
                date_match = re.search(r'Date Missing:\s*([^\n]+)', text)
                if date_match:
                    dt = NPSParser._parse_messy_date(date_match.group(1).strip())
                    record['date_missing'] = dt

                # Extract Location (Missing from / Last seen)
                location_match = re.search(r'Missing from:\s*([^\n]+)', text)
                if location_match:
                    record['last_seen'] = location_match.group(1).strip()
                
                records.append(record)
            
        NPSParser.logger.info(f"Parsed {len(records)} records from NPS data.")
        self.df = pd.DataFrame(records)

    @staticmethod
    def _fix_month(date_str):
        months = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
        ]

        parts = date_str.split(" ", 1)
        if len(parts) < 2:
            return date_str
        month = parts[0]

        best = difflib.get_close_matches(month, months, n=1, cutoff=0.6)
        if best:
            if month != best[0]:
                NPSParser.logger.debug(f"Corrected month from '{month}' to '{best[0]}'")

            return best[0] + " " + parts[1]

        return date_str

    @staticmethod
    def _parse_messy_date(date_str):
        cleaned = NPSParser._fix_month(date_str)
        dt = date_parser.parse(cleaned, fuzzy=True)
        return dt.strftime("%m/%d/%Y")

if __name__ == "__main__":
    parser = NPSParser()

    parser.parse()
    parser.save_csv()