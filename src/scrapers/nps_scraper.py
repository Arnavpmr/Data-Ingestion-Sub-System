from .single_page_scraper import SinglePageScraper

if __name__ == "__main__":
    s = SinglePageScraper(
        "nps",
        "https://www.nps.gov/orgs/1563/cold-cases.htm"
    )

    html = s.fetch_page()
    s.save_page(html)