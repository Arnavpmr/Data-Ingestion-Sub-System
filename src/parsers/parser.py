import os
from datetime import datetime

from abc import ABC, abstractmethod

from utils import get_latest_dir

class Parser(ABC):
    def __init__(self, name):
        self.name = name
        self.df = None
        self.input_dir = get_latest_dir(f"data/raw/{self.name}")

    @abstractmethod
    def parse(self):
        pass

    def save_csv(self):
        today = datetime.now().strftime("%Y-%m-%d")
        output_dir = os.path.join(f'data/silver/{self.name}/{today}')

        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f'{self.name}.csv')
        self.df.to_csv(output_path, index=False)