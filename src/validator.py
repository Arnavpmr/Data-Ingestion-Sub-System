import os
import pandas as pd
from collections import Counter

from typing import Optional, List
from pydantic import BaseModel, field_validator, ValidationError

from datetime import datetime
from utils import get_latest_dir

import dedupe


class PersonRecord(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    date_missing: Optional[str] = None
    last_seen: Optional[str] = None


    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("Name cannot be empty.")
        return v

    @field_validator("age", mode="before")
    @classmethod
    def parse_age(cls, v):
        try:
            return int(v)
        except:
            return None

    @field_validator("date_missing", mode="before")
    @classmethod
    def normalize_dates(cls, v):
        try:
            datetime.strptime(v, "%m/%d/%Y")
            return v
        except ValueError:
            raise ValueError("date_missing must be in MM/DD/YYYY format")

def validate_table(df: pd.DataFrame) -> pd.DataFrame:
    target_cols = ["name", "age", "gender", "date_missing", "last_seen"]
    available_cols = [c for c in target_cols if c in df.columns]
    required_if_exists = ["name", "date_missing", "last_seen"]

    clean_rows = []

    for _, row in df.iterrows():
        missing_required = [
            col for col in required_if_exists
            if col in available_cols and (pd.isna(row[col]) or row[col] == "")
        ]

        if missing_required: continue

        row_dict = row.to_dict()
        partial_row = {k: (v if not pd.isna(v) else None) for k, v in row_dict.items()}

        try:
            record = PersonRecord(**partial_row)
            clean_rows.append(record.model_dump())
        except ValidationError as e:
            raise ValueError(f"Validation error in row: {row}\n{e}")

    return pd.DataFrame(clean_rows, columns=target_cols)

def validate_and_combine_tables(list_of_dfs: List[pd.DataFrame]) -> pd.DataFrame:
    validated = [validate_table(df) for df in list_of_dfs]
    return pd.concat(validated, ignore_index=True)

def choose_best(values):
    """Select best value from duplicates column list."""
    # Remove missing markers
    clean = [v for v in values if v not in ("__MISSING__", "", None, float("nan"))]

    if not clean:
        return None

    # If numeric (age)
    if all(str(v).isdigit() for v in clean):
        return Counter(clean).most_common(1)[0][0]

    # If strings → pick longest (more info)
    return max(clean, key=lambda x: len(str(x)))

def merge_cluster(records):
    """Merge several dict rows into one canonical row."""
    merged = {}
    all_keys = set().union(*records)

    for key in all_keys:
        merged[key] = choose_best([rec.get(key) for rec in records])

    return merged

if __name__ == "__main__":
    dfs = []

    for dir in os.listdir("data/silver"):
        dir_path = get_latest_dir(os.path.join("data/silver", dir))

        if not os.path.isdir(dir_path):
            continue

        file = os.listdir(dir_path)[0]
        file_path = os.path.join(dir_path, file)
        df = pd.read_csv(file_path)
        dfs.append(df)

    combined_df = validate_and_combine_tables(dfs)

    combined_df = combined_df.fillna("__MISSING__")
    combined_df['age'] = combined_df['age'].apply(lambda x: str(x))
    data_dict = combined_df.to_dict(orient="index")

    with open("dedupe/settings_file", "rb") as sf:
        deduper = dedupe.StaticDedupe(sf)
    
    print("clustering...")
    clustered_dupes = deduper.partition(data_dict, 0.5)

    print("# duplicate sets", len(clustered_dupes))

    merged_rows = []
    for cluster_id, (record_ids, scores) in enumerate(clustered_dupes):
        records = [data_dict[int(rid)] for rid in record_ids]
        merged = merge_cluster(records)
        merged_rows.append(merged)
    
    final_df = pd.DataFrame(merged_rows)
    final_df.to_csv("data/gold/merged_validated_records.csv", index=False)

    # dedupe_fields = [
    #     dedupe.variables.String("name"),
    #     dedupe.variables.String("age", has_missing=True),
    #     dedupe.variables.Exact("gender", has_missing=True),
    #     dedupe.variables.String("date_missing", has_missing=True),
    #     dedupe.variables.String("last_seen", has_missing=True),
    # ]

    # deduper = dedupe.Dedupe(dedupe_fields)
    # deduper.prepare_training(data_dict)
    # dedupe.console_label(deduper)
    # deduper.train()

    # with open("training.json", "w") as tf:
    #     deduper.write_training(tf)

    # with open("settings_file", "wb") as sf:
    #     deduper.write_settings(sf)

