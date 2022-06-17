import unittest
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse


class TestIndex(unittest.TestCase):

    def test_index_html(self):
        url = "https://www.theverge.com/"

        HEADERS = ({'User-Agent':
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                        (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', \
                    'Accept-Language': 'en-US, en;q=0.5'})

        html_text = requests.get(url, headers=HEADERS).text
        html_text = html_text.replace(">", ">\n")
        with open(f"index.html", "w") as f:
            f.write(html_text)

        text = BeautifulSoup(html_text).get_text()
        with open("index.txt", "w") as f:
            f.write(text)


    def test_selectors(self):
        with open("notes", "r") as f:
            content = f.read()
            soup = BeautifulSoup(content)
            global_header_links = soup.select("nav ul li")
            pass

    def test_selectors(self):
        with open("index.html", "r") as f:
            content = f.read()
            soup = BeautifulSoup(content)
            header_section_search_result = soup.select('section.c-nav-list')
            if len(header_section_search_result) == 0:
                raise ValueError("")

            header_section = header_section_search_result[0]
            r = header_section.select("li")

            assert len(r) > 0

            li_dict = dict()
            active_folder = ""
            for li in r:
                folder = li.get("data-nav-item-id")
                if folder is not None:
                    active_folder = folder
                    li_dict[active_folder] = []
                else:
                    href = li.select("a")[0].get("href")
                    li_dict[active_folder].append(href)
            pass



