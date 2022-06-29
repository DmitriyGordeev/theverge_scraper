import unittest
from scraper import *
import os

class TestScraper(unittest.TestCase):

    def test_compare_topics_with_db(self):
        scraper = Scraper()
        scraper.find_main_menu_links()
        scraper.write_topics_update_file()


    def test_together(self):
        print ("scrape_topics.py")
        os.system("python scrape_topics.py")

        print("insert_topics.py")
        os.system("python insert_topics.py")

        print("scrape_articles.py")
        os.system("python scrape_articles.py")

        print("insert_articles.py")
        os.system("python insert_articles.py")