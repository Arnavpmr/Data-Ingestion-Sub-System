import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi

from datetime import datetime
import pandas as pd

from log_config import get_logger

def fetch_kaggle_data():
    logger = get_logger(module_name=__name__)

    api = KaggleApi()
    api.authenticate()

    cur_date = datetime.now().strftime("%Y-%m-%d")
    api.dataset_download_file("thesagentist/open-missing-person-cases-inside-national-parks",
                            "victims_coords.csv",
                            path=f"data/raw/kaggle/{cur_date}")