import pandas as pd
from collections import Counter

import dedupe

from log_config import get_logger

logger = get_logger(module_name=__name__)

def choose_best(values):
    """Select best value from duplicates column list."""
    # Remove missing markers
    clean = [v for v in values if v not in ("__MISSING__", "", None, float("nan"))]

    if not clean: return None

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
        logger.debug(f"Merging records with values: {[rec.get(key) for rec in records]}")
        merged[key] = choose_best([rec.get(key) for rec in records])

    return merged

def dedupe_data(df):
    df = df.fillna("__MISSING__")
    df['age'] = df['age'].apply(lambda x: str(x))
    data_dict = df.to_dict(orient="index")

    with open("dedupe/settings_file", "rb") as sf:
        deduper = dedupe.StaticDedupe(sf)
    
    clustered_dupes = deduper.partition(data_dict, 0.5)

    logger.info(f"Merging {len(clustered_dupes)} duplicate clusters")

    merged_rows = []
    for _, (record_ids, _) in enumerate(clustered_dupes):
        records = [data_dict[int(rid)] for rid in record_ids]
        merged = merge_cluster(records)
        merged_rows.append(merged)
    
    return pd.DataFrame(merged_rows)