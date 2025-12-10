import pytest
import pandas as pd
from src.parsers.locationsunknown_parser import LocationsUnknownParser

def test_locationsunknown_parse_method(tmp_path):
    # Create fake HTML file
    html_content = """
<a href="https://locationsunknown.org/case-list/david-michael-burney" target="_blank">–&nbsp;06-29-2007 – David Michael Burney – Bankhead Forest</a><br><a href="https://locationsunknown.org/case-list/james-taylor-wall" target="_blank">–&nbsp;01-25-2015 – James Taylor Wall – Bankhead National Forest</a><br>– 12-25-2020 – Yvonne Wood Covington – Little River Canyon National Preserve</p>
    """

    # Make directory + file
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    file_path = input_dir / "locationsunknown.html"
    file_path.write_text(html_content, encoding="utf-8")

    # Monkeypatch parser.input_dir so it reads from tmp_path
    parser = LocationsUnknownParser()
    parser.input_dir = str(input_dir)

    # Run parse()
    parser.parse()

    # Validate DataFrame content
    assert isinstance(parser.df, pd.DataFrame)
    assert len(parser.df) == 3

    assert list(parser.df.columns) == ["date_missing", "name", "last_seen"]

    # Verify correct normalization and field extraction
    assert parser.df.iloc[0]["date_missing"] == "06/29/2007"
    assert parser.df.iloc[0]["name"] == "David Michael Burney"
    assert parser.df.iloc[0]["last_seen"] == "Bankhead Forest"

    assert parser.df.iloc[1]["date_missing"] == "01/25/2015"
    assert parser.df.iloc[1]["name"] == "James Taylor Wall"
    assert parser.df.iloc[1]["last_seen"] == "Bankhead National Forest"

    assert parser.df.iloc[2]["date_missing"] == "12/25/2020"
    assert parser.df.iloc[2]["name"] == "Yvonne Wood Covington"
    assert parser.df.iloc[2]["last_seen"] == "Little River Canyon National Preserve"