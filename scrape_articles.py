from html_parser import *
import json
from postgre_db_interface import *
from scraper import *


if __name__ == "__main__":

    f = open("topic2articles.json", "r")
    topics2articles = json.loads(f.read())
    f.close()

    theVergeScraper = Scraper()
    theVergeScraper.loop_through_articles(topics2articles)















