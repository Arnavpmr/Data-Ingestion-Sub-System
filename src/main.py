from log_config import setup_logging, get_logger

from scrapers.single_page_scraper import SinglePageScraper
from scrapers.missingnpf_scraper import scrape_all_profiles

from parsers.locationsunknown_parser import LocationsUnknownParser
from parsers.nps_parser import NPSParser
from parsers.missingnpf_parser import MissingNPFParser
from parsers.yosemite_pdf_parser import parse_yosemite_pdf

from fetch_kaggle import fetch_kaggle_data
from transform.clean_kaggle import clean_kaggle_data

from transform.validator import validate_all_data, validate_table, clean_insufficient_rows

from transform.deduper import dedupe_data
from transform.enricher import fill_gender

from load_postgres import load_to_postgres

# Finalized schema
# name, age, gender, date_missing (MM-DD-YYYY), last_seen, lat, long

def main():
    # Setup logging
    setup_logging()
    logger = get_logger(module_name=__name__)

    # # Initialize single-page scrapers
    # single_page_scrapers = [
    #     SinglePageScraper(
    #         name="locationsunknown",
    #         base_url="https://locationsunknown.org/the-missing-list"
    #     ),
    #     SinglePageScraper(
    #         name="nps",
    #         base_url="https://www.nps.gov/orgs/1563/cold-cases.htm"
    #     )
    # ]

    # logger.info("Starting scraping process.")

    # # Run single-page scrapers
    # for scraper in single_page_scrapers:
    #     logger.info(f"Fetching page for {scraper.name}")
    #     html = scraper.fetch_page()
    #     scraper.save_page(html)
    #     logger.info(f"Saved page for {scraper.name}")
    
    # # Run multi-page scraper for Missing NPF
    # logger.info("Starting multi-page scraping for Missing NPF profiles.")
    # scrape_all_profiles(start_page=1, delay=1.0)

    # logger.info("Fetching kaggle data.")
    # fetch_kaggle_data()
    # logger.info("Kaggle data fetched successfully.")

    # logger.info("Scraping and data fetching process completed! Beginning parsing and validation.")

    # Initialize parsers
    parsers = [
        LocationsUnknownParser(),
        NPSParser(),
        MissingNPFParser(),
    ]

    # Run parsers
    for parser in parsers:
        logger.info(f"Parsing data for {parser.name}")
        parser.parse()
        parser.save_csv()
        logger.info(f"Saved CSV for {parser.name}")
    
    logger.info("Parsing Yosemite pdf data")
    parse_yosemite_pdf()
    
    logger.info("Cleaning kaggle data")
    clean_kaggle_data()

    # Validate, standardize, and merge all data sources
    logger.info("Parsing and cleaning completed. Beginning data validation and merging.")
    validated_df = validate_all_data()
    logger.info("Data validation and merging completed.")

    # Deduplicate data with ml
    logger.info("Deduplicating data")
    deduped_data = dedupe_data(validated_df)
    logger.info("Deduplication completed.")

    # Final cleaning to remove rows with insufficient data
    logger.info("Cleaning deduped data")
    final_data = clean_insufficient_rows(deduped_data)
    logger.info("Final data cleaning completed.")

    # Enrich data by filling in missing genders from names (gender-guesser)
    logger.info("Enriching data by filling missing genders")
    final_data = fill_gender(final_data)
    logger.info("Gender enrichment completed.")

    # Load data into postgresql
    logger.info("Loading data into postgres")
    load_to_postgres(final_data)
    logger.info(f"Loaded {len(final_data)} records into postgres!")

if __name__ == "__main__":
    main()