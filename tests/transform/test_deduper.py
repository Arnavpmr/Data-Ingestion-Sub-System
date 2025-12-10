import pytest
import pandas as pd
from collections import Counter
from unittest.mock import patch, MagicMock
from src.transform.deduper import (
    choose_best,
    merge_cluster,
    dedupe_data
)

def test_choose_best_numeric():
    values = ["1", "2", "2", "3"]
    assert choose_best(values) == "2"

def test_choose_best_strings():
    values = ["short", "longer_string", "medium"]
    assert choose_best(values) == "longer_string"

def test_choose_best_with_missing_values():
    values = ["", None, "__MISSING__", "valid"]
    assert choose_best(values) == "valid"

def test_choose_best_all_missing():
    values = ["", None, "__MISSING__"]
    assert choose_best(values) is None


def test_merge_cluster_basic():
    records = [
        {"name": "Alice", "age": "30"},
        {"name": "Alice A.", "age": "30"},
        {"name": "Alice", "age": "31"}
    ]

    merged = merge_cluster(records)
    assert merged["name"] == "Alice A."
    assert merged["age"] == "30"

def test_merge_cluster_missing_values():
    records = [
        {"name": None, "age": ""},
        {"name": "__MISSING__", "age": None},
        {"name": "Bob", "age": "25"}
    ]

    merged = merge_cluster(records)
    assert merged["name"] == "Bob"
    assert merged["age"] == "25"

def test_merge_cluster_different_keys():
    records = [
        {"name": "Alice"},
        {"age": "30"},
        {"gender": "F"}
    ]

    merged = merge_cluster(records)
    assert merged["name"] == "Alice"
    assert merged["age"] == "30"
    assert merged["gender"] == "F"