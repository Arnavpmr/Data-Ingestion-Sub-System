# Missing Persons Data Ingestion Pipeline

## Overview

This project is an end‑to‑end ETL/ELT data ingestion system that
consolidates missing‑persons information from multiple heterogeneous
sources --- scraped websites, PDFs, and Kaggle datasets --- into a
unified cleaned dataset suitable for analytics and storage in
PostgreSQL.

## Key Features

-   **Automated Web Scraping**
    -   Custom scraper + parser class for each website source
    -   BeautifulSoup + regex extraction
    -   Raw HTML stored in *bronze* layer
    -   Cleaned, parsed CSVs stored in *silver* layer
    -   Fuzzy date correction for misspellings (e.g., *Ocbtober →
        October*)
-   **PDF Table Extraction**
    -   Tabula to extract structured tables
    -   Standardization of dates, columns, and formats
    -   Output stored in silver layer as CSV
-   **Kaggle Dataset Ingestion**
    -   KaggleHub API for downloading datasets
    -   Stored directly in *bronze* layer
-   **Validation & Standardization**
    -   Pydantic schema enforcing required fields
    -   Optional fields coerced (age → int)
    -   Dataset‑specific rules respected (required fields only enforced
        if present)
    -   Invalid rows logged to `debug.log`
-   **Deduplication & Record Linking**
    -   Dedupe.io ML‑powered clustering
    -   Merges duplicate clusters by selecting rows with highest
        information completeness
    -   Final merged table cleaned again to ensure all required columns
        are present
-   **PostgreSQL Loading**
    -   SQLAlchemy UPSERT logic
    -   Final "gold" table stored in PostgreSQL

## Architecture

Bronze → Silver → Gold layered architecture: 1. **Bronze:** Raw HTML,
raw PDFs, raw Kaggle files
2. **Silver:** Parsed + standardized tables
3. **Gold:** Deduped, validated, merged final dataset

## Logging

-   Structured logging config
-   `app.log`: standard pipeline logs
-   `error.log`: errors only
-   `debug.log`: rejected rows and validation failures

## Tech Stack

Python, BeautifulSoup, regex, Tabula, pandas, pydantic, dedupe.io,
SQLAlchemy, PostgreSQL.
