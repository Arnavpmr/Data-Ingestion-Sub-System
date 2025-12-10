import pytest
import pandas as pd
from unittest.mock import patch, mock_open, MagicMock
from pydantic import ValidationError

from src.transform.validator import (
    PersonRecord, 
    clean_insufficient_rows, 
    validate_table, 
    validate_and_combine_tables,
    validate_all_data
)


def test_clean_insufficient_rows():
    df = pd.DataFrame([
        {"name": "John", "date_missing": "01/01/2020", "last_seen": "NYC"},
        {"name": "", "date_missing": "01/01/2020", "last_seen": "NYC"},
        {"name": "Anna", "date_missing": "", "last_seen": "NYC"},
        {"name": "Mike", "date_missing": "01/01/2020", "last_seen": ""}
    ])

    clean_df = clean_insufficient_rows(df)

    assert len(clean_df) == 1
    assert clean_df.iloc[0]["name"] == "John"

def test_personrecord_date_invalid():
    with pytest.raises(ValidationError):
        PersonRecord(
            name="Bob",
            date_missing="2020-01-01",
            last_seen="Store"
        )

def test_validate_table_valid():
    df = pd.DataFrame([
        {"name": "John", "age": "30", "gender": "M", "date_missing": "01/01/2020", "last_seen": "NYC"}
    ])

    clean_df = validate_table(df)
    assert len(clean_df) == 1
    assert clean_df.iloc[0]["age"] == 30

def test_validate_and_combine_tables():
    df1 = pd.DataFrame([
        {"name": "John", "age": "30", "gender": "M",
         "date_missing": "01/01/2020", "last_seen": "NYC"}
    ])
    df2 = pd.DataFrame([
        {"name": "Anna", "age": "25", "gender": "F",
         "date_missing": "02/01/2020", "last_seen": "Boston"}
    ])

    combined = validate_and_combine_tables([df1, df2])

    assert len(combined) == 2
    assert set(combined["name"]) == {"John", "Anna"}

@patch("os.listdir")
@patch("src.utils.get_latest_dir")
@patch("pandas.read_csv")
@patch("os.path.isdir")
def test_validate_all_data(
    mock_isdir, mock_read_csv, mock_get_latest, mock_listdir
):
    mock_listdir.return_value = ["source1", "source2"]
    mock_isdir.return_value = True
    mock_get_latest.side_effect = lambda p: f"{p}/2025-01-01"

    mock_read_csv.return_value = pd.DataFrame([
        {
            "name": "John",
            "age": "33",
            "gender": "M",
            "date_missing": "01/01/2020",
            "last_seen": "Chicago"
        }
    ])

    combined = validate_all_data()

    assert len(combined) == 2
    assert all(combined["age"] == 33)