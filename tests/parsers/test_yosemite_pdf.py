import pytest
from unittest.mock import patch
import pandas as pd
from datetime import datetime

from src.parsers.yosemite_pdf_parser import parse_yosemite_pdf


def fake_df():
    return pd.DataFrame({
        "First": ["John", "Sarah"],
        "Last": ["Doe", "Lee"],
        "Last Known Point": ["Valley Floor", "Glacier Point"],
        "Date": ["2023-01-10", "2021-09-03"]
    })


def test_no_tables_found(monkeypatch):
    monkeypatch.setattr("tabula.read_pdf", lambda *a, **kw: [])

    with pytest.raises(ValueError):
        parse_yosemite_pdf()

def test_parses_pdf_correctly(monkeypatch, tmp_path):
    monkeypatch.setattr("tabula.read_pdf", lambda *a, **kw: [fake_df()])

    output_dir = tmp_path / "silver/yosemite_pdf/2024-01-01"
    output_dir.mkdir(parents=True)

    with patch("parsers.yosemite_pdf_parser.datetime") as mock_dt:
        mock_dt.now.return_value = mock_dt.strptime("2024-01-01", "%Y-%m-%d")
        mock_dt.strftime = datetime.strftime

        def fake_path_constructor(path_str):
            return output_dir / "missing_persons_yosemite.csv"

        monkeypatch.setattr("parsers.yosemite_pdf_parser.Path", fake_path_constructor)
        saved_df = {}

        def fake_to_csv(self, path, index):
            saved_df["data"] = self.copy()

        monkeypatch.setattr(pd.DataFrame, "to_csv", fake_to_csv)

        parse_yosemite_pdf()

    df = saved_df["data"]

    assert "name" in df.columns
    assert df.loc[0, "name"] == "John Doe"
    assert df.loc[1, "name"] == "Sarah Lee"

    assert df.loc[0, "last_seen"].endswith("Yosemite National Park")

    assert df.loc[0, "date_missing"] == "01/10/2023"
    assert df.loc[1, "date_missing"] == "09/03/2021"