import unittest
from postgre_db_interface import *
import psycopg2
import pandas
from scraper import Scraper


class TestPostgreDBInterface(unittest.TestCase):

    def test_get_num_existing_articles_from_db(self):
        scraper = Scraper()
        pdb = scraper.db_interface
        r = pdb.get_num_existing_articles_from_db()
        print (r)
        pass


    def test_db_interface_get_topics_from_db(self):
        scraper = Scraper()
        pdb = scraper.db_interface
        print (pdb.get_topics_from_db())


    def test_get_the_last_article_time(self):
        scraper = Scraper()
        pdb = scraper.db_interface
        # ERROR - что записывает topics2articles.json
        print(pdb.get_last_article_time())


    def test_config(self):
        r = PostgreDBInterface.config()
        pass



