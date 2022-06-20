import re
import unittest
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
from html_parser import Parser


class TestIndex(unittest.TestCase):

    def test_index_html(self):
        url = "https://www.theverge.com/21546591/best-amazon-echo-deals"

        HEADERS = ({'User-Agent':
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                        (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', \
                    'Accept-Language': 'en-US, en;q=0.5'})

        html_text = requests.get(url, headers=HEADERS).text
        html_text = html_text.replace(">", ">\n")
        with open(f"article.html", "w") as f:
            f.write(html_text)

        # text = BeautifulSoup(html_text).get_text()
        # with open("tech.txt", "w") as f:
        #     f.write(text)


    def test_main_menu_header_links(self):
        with open("index.html", "r") as f:
            content = f.read()
            # soup = BeautifulSoup(content)
            # header_section_search_result = soup.select('section.c-nav-list')
            # if len(header_section_search_result) == 0:
            #     raise ValueError("")
            #
            # header_section = header_section_search_result[0]
            # r = header_section.select("li")
            #
            # assert len(r) > 0
            #
            # folder2href = dict()
            # active_folder = ""
            # for li in r:
            #     folder = li.get("data-nav-item-id")
            #     if folder is not None:
            #         active_folder = folder
            #         folder2href[active_folder] = []
            #     else:
            #         href = li.select("a")[0].get("href")
            #         folder2href[active_folder].append(href)

            links = Parser.parse_main_menu_links(content)
            pass


    def test_find_folder_links(self):
        with open("tech.html", "r") as f:
            content = f.read()
            # soup = BeautifulSoup(content)
            # r = soup.select("div.l-segment.l-main-content "
            #                 "div.c-compact-river__entry "
            #                 "a.c-entry-box--compact__image-wrapper")
            # links = []
            # for a in r:
            #     links.append(a.get("href"))
            # pass

            links = Parser.find_selected_folder_links(content)
            pass


    def test_parse_article(self):
        with open("article.html", "r") as f:
            content = f.read()
            # soup = BeautifulSoup(content)
            # header_wrap = soup.select("article.l-main-content "
            #                           "div.c-entry-hero__header-wrap")
            #
            # if len(header_wrap) == 0:
            #     raise RuntimeError("no item found")
            #
            # header_text = header_wrap[0].select("h1")[0].text
            # summary_text = soup.select("article.l-main-content p.c-entry-summary")[0].text
            # authors_and_time = soup.select("article.l-main-content div.c-byline")[0].text
            # authors_and_time = authors_and_time.replace("\n", "")
            # authors_and_time = re.sub("\s{2,}", " ", authors_and_time).strip()
            #
            # # article's content - select all p and h2 where the main text resides
            # entry_content = soup.select("div.c-entry-content")
            # main_text_tags = entry_content[0].select("h2, p[id]")
            # content = ""
            # for t in main_text_tags:
            #     content += t.text
            # with open("content.txt", "w", encoding="utf-8") as fw:
            #     fw.write(content)
            #
            # # References inside the article:
            # refs = entry_content[0].select("a")
            # pass

            article_result = Parser.parse_article_page(content)
            pass


    def test_get_time(self):
        with open("article.html", "r") as f:
            content = f.read()
            soup = BeautifulSoup(content)

            times = soup.select("time")
            time = ""
            if len(times) > 0:
                time = times[0].get("datetime")
            pass



