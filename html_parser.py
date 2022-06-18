import re
import unittest
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse


class ArticleResult:
    def __init__(self):
        self.url = ""
        self.header = ""
        self.summary = ""
        self.byline = ""
        self.time = ""
        self.main_text = ""
        self.inner_links = []


class Parser:

    @staticmethod
    def parse_main_menu_links(html):
        """ Returns a dict with key(str)=FolderName ('tech', 'science', ..)
         and value(list)=[links] """
        soup = BeautifulSoup(html)
        header_section_search_result = soup.select('section.c-nav-list')
        if len(header_section_search_result) == 0:
            raise ValueError("")

        header_section = header_section_search_result[0]
        r = header_section.select("li")

        # TODO: change assert to ..? !
        assert len(r) > 0

        folder2href = dict()
        active_folder = ""
        for li in r:
            folder = li.get("data-nav-item-id")
            if folder is not None:
                active_folder = folder
                folder2href[active_folder] = []
            else:
                href = li.select("a")[0].get("href")
                folder2href[active_folder].append(href)
        return folder2href


    @staticmethod
    def find_selected_folder_links(html):
        """ Returns a list of links to concrete articles """
        soup = BeautifulSoup(html)
        r = soup.select("div.l-segment.l-main-content "
                        "div.c-compact-river__entry "
                        "a.c-entry-box--compact__image-wrapper")
        links = []
        for a in r:
            links.append(a.get("href"))
        return links


    @staticmethod
    def parse_article_page(html):
        soup = BeautifulSoup(html)
        header_wrap = soup.select("article.l-main-content "
                                  "div.c-entry-hero__header-wrap")

        if len(header_wrap) == 0:
            raise RuntimeError("no item found")

        header_text = header_wrap[0].select("h1")[0].text
        summary_text = soup.select("article.l-main-content p.c-entry-summary")[0].text
        authors_and_time = soup.select("article.l-main-content div.c-byline")[0].text
        authors_and_time = authors_and_time.replace("\n", "")
        authors_and_time = re.sub("\s{2,}", " ", authors_and_time).strip()

        # article's content - select all p and h2 where the main text resides
        entry_content = soup.select("div.c-entry-content")
        main_text_tags = entry_content[0].select("h2, p[id]")
        main_text = ""
        for t in main_text_tags:
            main_text += t.text
        with open("content.txt", "w", encoding="utf-8") as fw:
            fw.write(main_text)

        # References inside the article:
        refs = entry_content[0].select("a")

        article = ArticleResult()
        article.header = header_text
        article.summary = summary_text
        article.time = ""   # todo
        article.byline = authors_and_time
        article.main_text = main_text
        article.inner_links = refs

        return article



