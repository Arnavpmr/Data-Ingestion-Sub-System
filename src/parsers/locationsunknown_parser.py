import re
import pandas as pd

from parsers.parser import Parser
from log_config import get_logger

class LocationsUnknownParser(Parser):
    def __init__(self):
        super().__init__("locationsunknown")

    def parse(self):
        logger = get_logger(module_name=__name__)

        with open(f"{self.input_dir}/{self.name}.html", "r", encoding="utf-8") as f:
            logger.debug("Reading HTML file for Locations Unknown parser.")
            data_string = f.read()

        pattern = r'(\d{2}-\d{2}-\d{4})\ [–-]\ ([^–]+?)\ [–-]\ ([^<]+)'

        matches = re.findall(pattern, data_string)
        logger.debug(f"Regex found {len(matches)} matches in Locations Unknown data.")

        normalized_matches = [(date.replace("-", "/"), name, loc) for date, name, loc in matches]
        logger.debug("Normalized date formats in matches.")

        self.df = pd.DataFrame(normalized_matches, columns=['date_missing', 'name', 'last_seen'])
        logger.info(f"Parsed {len(self.df)} records from Locations Unknown data.")

if __name__ == "__main__":
    parser = LocationsUnknownParser()

    parser.parse()
    parser.save_csv()