import re
import pandas as pd

from ..parser import Parser

class LocationsUnknownParser(Parser):
    def __init__(self):
        super().__init__("locationsunknown")

    def parse(self):
        with open(f"{self.input_dir}/{self.name}.html", "r", encoding="utf-8") as f:
            data_string = f.read()

        pattern = r'(\d{2}-\d{2}-\d{4})\ [–-]\ ([^–]+?)\ [–-]\ ([^<]+)'
        matches = re.findall(pattern, data_string)
        normalized_matches = [(date.replace("-", "/"), name, loc) for date, name, loc in matches]

        self.df = pd.DataFrame(normalized_matches, columns=['date_missing', 'name', 'last_seen'])

if __name__ == "__main__":
    parser = LocationsUnknownParser()

    parser.parse()
    parser.save_csv()