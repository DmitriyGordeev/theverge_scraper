import re
import unittest
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
from html_parser import Parser
import datetime


class TestIndex(unittest.TestCase):

    def test_index_html(self):
        url = "https://www.theverge.com/good-deals/2022/6/29/23186904/samsung-980-pro-m2-ssd-ps5-google-nest-mini-chromecast-android-pixel-6-pro-deal-sale"

        HEADERS = ({'User-Agent':
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                        (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', \
                    'Accept-Language': 'en-US, en;q=0.5'})

        html_text = requests.get(url, headers=HEADERS).text
        html_text = html_text.replace(">", ">\n")
        with open(f"test_html_pages/article.html", "w") as f:
            f.write(html_text)

        soup = BeautifulSoup(html_text, "html.parser")
        pass
        # soup.select("section.c-two-up")[0].select(".c-entry-box-base__headline")[0].select("a")[0].get("href")


    def test_main_menu_header_links(self):
        with open("test_html_pages/index.html", "r") as f:
            content = f.read()
            folder2hrefs = Parser.parse_main_menu_links(content)
            pass


    def test_find_folder_links(self):
        with open("test_html_pages/tech.html", "r") as f:
            content = f.read()
            soup = BeautifulSoup(content, "html.parser")

            # Next button:
            next_ref = soup.select("a.c-pagination__next.c-pagination__link.p-button")

            links = Parser.find_links_on_selected_menu(content)
            pass


    def test_parse_article(self):
        with open("test_html_pages/article.html", "r") as f:
            content = f.read()
            article_result = Parser.parse_article_page(content)
            try:
                dt = datetime.datetime.strptime(article_result.time, "%Y-%m-%dT%H-%M:%S")
            except:
                print ("Error parsing time")
            pass


    def test_get_time(self):
        with open("article.html", "r") as f:
            content = f.read()
            soup = BeautifulSoup(content, "html.parser")

            times = soup.select("time")
            time = ""
            if len(times) > 0:
                time = times[0].get("datetime")
            pass


    def test_html_next_page(self):
        with open("tech_archives.html", "r") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            hrefs = soup.select("a.c-pagination__next.c-pagination__link.p-button")
            if len(hrefs) > 0:
                next_page_link = hrefs[0].get("href")


    def test_compress_string(self):
        header = "General Motors is using AI to speed up the vehicle inspection process"
        header = header.lower()
        words = header.split(" ")
        out = ''
        if len(words) > 2:
            out = '_'.join(words[:2])
        pass

