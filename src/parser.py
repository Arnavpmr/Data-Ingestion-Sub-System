import os
from datetime import datetime

from abc import ABC, abstractmethod

import pandas as pd

class Parser(ABC):
    def __init__(self, name, df: pd.DataFrame=None):
        self.name = name
        self.df = df
        self.input_dir = self.get_latest_dir()

    @abstractmethod
    def parse(self):
        pass

    def save_csv(self):
        today = datetime.now().strftime("%Y-%m-%d")
        output_dir = os.path.join(f'data/silver/{self.name}/{today}')

        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f'{self.name}.csv')
        self.df.to_csv(output_path, index=False)
    
    def get_latest_dir(self):
        base_dir = f"data/raw/{self.name}"
        date_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

        if not date_dirs:
            raise FileNotFoundError("No valid date directories found in raw missingnpf data.")

        latest_date = max(date_dirs)

        return os.path.join(base_dir, latest_date)