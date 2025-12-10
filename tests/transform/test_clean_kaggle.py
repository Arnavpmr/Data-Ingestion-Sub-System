import pytest
from unittest.mock import patch

from src.transform.clean_kaggle import clean_kaggle_data

@patch("pandas.DataFrame.to_csv")
def test_clean_valid_row_produces_output(mock_to_csv):
    clean_kaggle_data()

    # DataFrame should be written
    assert mock_to_csv.call_count == 1

    # Confirm output path built correctly
    args, _ = mock_to_csv.call_args
    output_path = args[0]
    assert "data/silver/kaggle/" in output_path
    assert output_path.endswith("kaggle.csv")
