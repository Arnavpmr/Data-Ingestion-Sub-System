import pytest

from bs4 import BeautifulSoup
import re

from src.parsers.nps_parser import NPSParser


def test_fix_month_correct_spelling():
    assert NPSParser._fix_month("January 5 2020") == "January 5 2020"

def test_fix_month_misspelled_month():
    fixed = NPSParser._fix_month("Januery 5 2020")
    assert fixed.startswith("January")

def test_fix_month_bad_format():
    assert NPSParser._fix_month("Januery") == "Januery"


def test_parse_messy_date_normalizes_date():
    result = NPSParser._parse_messy_date("January 5, 2020")
    assert result == "01/05/2020"

def test_parse_messy_date_handles_misspelling():
    result = NPSParser._parse_messy_date("Januery 5 2020")
    assert result == "01/05/2020"


@pytest.fixture
def parser():
    return NPSParser()

@pytest.fixture
def sample_html():
    return """
    <div class='Component ArticleTextGroup TextWrapped clearfix'>
        Name:  John   Doe
        Description: A 35 years old male last seen hiking.
        Date Missing: Januery 5 2020
        Missing from: Yosemite National Park
    </div>
    """

def test_extract_date_missing(sample_html):
    soup = BeautifulSoup(sample_html, "lxml")
    elem = soup.find("div")
    text = elem.get_text()

    date_match = re.search(r"Date Missing:\s*([^\n]+)", text)
    dt = NPSParser._parse_messy_date(date_match.group(1).strip())

    assert dt == "01/05/2020"

def test_full_parse(tmp_path):
    html = """
    <div class='Component ArticleTextGroup TextWrapped clearfix'>
        Name: Jane Smith
        Description: A 22 years old female last seen camping.
        Date Missing: February 10 2021
        Missing from: Zion National Park
    </div>
    """

    # create fake input directory and file
    input_dir = tmp_path
    file_path = input_dir / "nps.html"
    file_path.write_text(html, encoding="utf-8")

    parser = NPSParser()
    parser.input_dir = str(input_dir)

    parser.parse()

    df = parser.df

    assert len(df) == 1
    row = df.iloc[0]

    assert row["name"] == "Jane Smith"
    assert row["age"] == "22"
    assert row["gender"] == "F"
    assert row["date_missing"] == "02/10/2021"
    assert row["last_seen"] == "Zion National Park"