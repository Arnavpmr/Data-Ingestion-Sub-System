import os
import pandas as pd

from typing import Optional, List
from pydantic import BaseModel, field_validator, ValidationError

from datetime import datetime
from utils import get_latest_dir

from log_config import get_logger


logger = get_logger(module_name=__name__)

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
            logger.error(f"Failed to parse date_missing: {v}")
            raise ValueError("date_missing must be in MM/DD/YYYY format")

def clean_insufficient_rows(df):
    logger.debug("Cleaning rows with insufficient data.")
    required_cols = ["name", "date_missing", "last_seen"]
    clean_df = df.dropna(subset=required_cols)

    for col in required_cols:
        clean_df = clean_df[clean_df[col].str.strip() != ""]
    
    logger.debug(f"Rejected: {len(df) - len(clean_df)} rows dropped due to insufficient data.")

    return clean_df

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

        if missing_required:
            logger.debug(f"Rejected: Due to missing required fields\n{row}")
            continue

        row_dict = row.to_dict()
        partial_row = {k: (v if not pd.isna(v) else None) for k, v in row_dict.items()}

        try:
            record = PersonRecord(**partial_row)
            clean_rows.append(record.model_dump())
        except ValidationError as e:
            logger.debug(f"Rejected: Validation error in row: {row}\n{e}")
            raise ValueError(f"Validation error in row: {row}\n{e}")

    return pd.DataFrame(clean_rows, columns=target_cols)

def validate_and_combine_tables(list_of_dfs: List[pd.DataFrame]) -> pd.DataFrame:
    logger.debug("Validating and combining multiple data tables.")

    validated = [validate_table(df) for df in list_of_dfs]
    return pd.concat(validated, ignore_index=True)

def validate_all_data():
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

    return combined_df