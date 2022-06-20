import re
import unittest
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
from html_parser import Parser


class Scraper:
    def __init__(self):
        self.main_menu_links = []


    def requests_pipeline(self):
        # TODO: schedule different requests in right order here
        #   with random delay or different time lags, etc...
        pass


    def find_main_menu_links(self):
        root = "https://theverge.com"
        html = requests.get(root, headers=self.emulate_headers()).text
        self.main_menu_links = Parser.parse_main_menu_links(html)
        pass


    @staticmethod
    def emulate_headers():
        return ({'User-Agent':
                 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                 'Accept-Language': 'en-US, en;q=0.5'})