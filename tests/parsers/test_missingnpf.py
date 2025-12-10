import os
import pytest
from unittest.mock import mock_open, patch
from src.parsers.missingnpf_parser import MissingNPFParser
from bs4 import BeautifulSoup


@pytest.mark.parametrize("name,expected", [
    ("John Doe", False),
    ("Jane Doe", False),
    ("Unidentified Male", False),
    ("Random Person", True),
    ("Too Many Words In Name Test", False),
    ("A B", True),
])
def test_is_valid_name(name, expected):
    assert MissingNPFParser._is_valid_name(name) == expected


def test_name_to_url_basic():
    assert MissingNPFParser._name_to_url("John Smith") == "john-smith"

def test_name_to_url_with_parentheses():
    assert MissingNPFParser._name_to_url("Mary (Ann) Jones") == "mary-ann-jones"


FAKE_PAGE_HTML = """
<div class="ts-preview">
    <h3 class="elementor-heading-title">
        <a>John Smith</a>
    </h3>

    <span data-text="Reported Missing: January 1, 2020 (4 years ago)">
        Reported Missing: January 1, 2020 (4 years ago)
    </span>

    <ul class="premium-bullet-list-box">
        <li><a><span>New York City</span></a></li>
    </ul>
</div>
"""

FAKE_PROFILE_HTML = """
<ul class="elementor-icon-list-items">
    <li class="elementor-icon-list-item">Age: 34</li>
    <li class="elementor-icon-list-item">Gender/Sex: Male</li>
</ul>
"""


def test_parse_creates_dataframe(tmp_path):
    pages_dir = tmp_path / "pages"
    profiles_dir = tmp_path / "profiles"
    pages_dir.mkdir()
    profiles_dir.mkdir()

    page_file = pages_dir / "page1.html"
    page_file.write_text(FAKE_PAGE_HTML, encoding="utf-8")

    profile_file = profiles_dir / "john-smith.html"
    profile_file.write_text(FAKE_PROFILE_HTML, encoding="utf-8")

    parser = MissingNPFParser()
    parser.input_dir = str(tmp_path)

    parser.parse()

    assert parser.df is not None
    assert len(parser.df) == 1

    row = parser.df.iloc[0]

    assert row["name"] == "John Smith"
    assert row["last_seen"] == "New York City"
    assert row["age"] == "34"
    assert row["gender"] == "M"

    assert "date_missing" in parser.df.columns


def test_parse_skips_invalid_name(tmp_path):
    pages_dir = tmp_path / "pages"
    profiles_dir = tmp_path / "profiles"
    pages_dir.mkdir()
    profiles_dir.mkdir()

    invalid_html = """
    <div class="ts-preview">
        <h3 class="elementor-heading-title">
            <a>Unidentified Male</a>
        </h3>
    </div>
    """

    (pages_dir / "bad.html").write_text(invalid_html, encoding="utf-8")

    parser = MissingNPFParser()
    parser.input_dir = str(tmp_path)
    parser.parse()

    assert len(parser.df) == 0