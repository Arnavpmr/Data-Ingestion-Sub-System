import pandas as pd
import csv

from pydantic import BaseModel, ValidationError, field_validator, Field
from typing import Optional

import os
from datetime import datetime
from utils import get_latest_dir


class Victim(BaseModel):
    name: str
    age: Optional[int] = Field(None, ge=0, le=120)
    park: str

    @field_validator('name', 'park')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise ValueError('name must be a non-empty string')
        return v
    
    # if age is a string, return None
    @field_validator('age', mode='before')
    @classmethod
    def validate_age(cls, v):
        try:
            if int(v): return v
        except ValueError:
            return None

def clean_csv():
    # name,age,park,state,year,notes,latitude,longitude
    EXPECTED_COLS = 8  

    clean_rows = []
    input_dir = get_latest_dir("/data/raw/kaggle")
    input_path = os.path.join(input_dir, "victims_coords.csv")

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)

        for line_num, row in enumerate(reader):
            if line_num == 0: continue

            if len(row) != EXPECTED_COLS:
                continue

            name, age, park, *_ = row  # only the first 3 matter
            try:
                victim = Victim(name=name, age=age, park=park)
                clean_rows.append({'name': victim.name, 'age': victim.age, 'last_seen': victim.park})
            except ValidationError as e:
                print(e, f"on line {line_num}")
                continue
    
    df = pd.DataFrame(clean_rows)

    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join(f'data/silver/kaggle/{today}')

    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "kaggle.csv"), index=False)

if __name__ == "__main__":
    clean_csv()