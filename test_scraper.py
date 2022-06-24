import unittest
from scraper import *


class TestScraper(unittest.TestCase):

    def test_compare_topics_with_db(self):
        scraper = Scraper()
        scraper.find_main_menu_links()
        scraper.write_topics_update_file()