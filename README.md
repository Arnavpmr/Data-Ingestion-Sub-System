# Ingestion

## Overview
The Ingestion project is a data pipeline solution designed to extract, process, and load data from various sources into target systems.

## Features
- Multi-source data extraction
- Data validation and transformation
- Error handling and logging
- Configurable ingestion workflows

## Getting Started
1. Clone the repository
2. Install dependencies: `npm install` or `pip install -r requirements.txt`
3. Configure your data sources in `config.yml`
4. Run the ingestion pipeline: `npm start` or `python main.py`

## Project Structure
```
├── src/
├── config/
├── tests/
└── docs/
```

## Challenges
Web scraping
    Data is formatted very different from site to site
    Names can be slightly mispelled or vary which makes it challenging to consolidate data
    Website used a mix of hyphens and dashes which took a while for me to catch during scraping

Important Notes
Do not train dedupe with vscode's debugger as it interferes with stuff
Run validator.py in the terminal