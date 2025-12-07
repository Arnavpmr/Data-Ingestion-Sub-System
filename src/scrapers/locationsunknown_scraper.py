from ..single_page_scraper import SinglePageScraper

if __name__ == "__main__":
    s = SinglePageScraper(
        name="locationsunknown",
        base_url="https://locationsunknown.org/the-missing-list"
    )

    html = s.fetch_page()
    s.save_page(html)