from scraper import *


def main():
    theVergeScraper = Scraper()
    # theVergeScraper.find_main_menu_links()
    theVergeScraper.requests_pipeline()


if __name__ == "__main__":
    main()