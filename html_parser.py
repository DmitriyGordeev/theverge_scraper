import re
import unittest
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse


class ArticleResult:
    def __init__(self):
        self.url = ""
        self.tags = []
        self.header = ""
        self.summary = ""
        self.byline = ""
        self.time = ""
        self.main_text = ""
        self.inner_links = []
        self.parsing_error = ""

    def formatted_text(self):
        output = ""
        output += f"url: {self.url}\n\n"
        output += f"{self.header}\n\n"
        output += f"{self.summary}\n\n"
        output += f"{self.tags}\n\n"
        output += f"{self.byline}\n\n"
        output += f"{self.main_text}"
        return output


    def to_json_string(self):
        out = dict()
        out["url"] = self.url
        out["title"] = self.header
        out["content"] = self.main_text
        out["dt"] = self.time
        out["tags"] = self.tags
        return json.dumps(out, indent=4)


    def short(self):
        header = self.header.lower()
        header = re.sub('[^a-zA-Z ]+', '', header)
        words = header.split(" ")
        out = ''
        if len(words) > 2:
            out = '_'.join(words[:2])
        out = out + "_" + self.time
        out = out.replace(":", "")
        return out


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

        folder2submenu_urls = dict()
        folder2url  = dict()
        active_folder = ""
        for li in r:
            folder = li.get("data-nav-item-id")
            a = li.select("a")
            folder_link = ""
            if len(a) > 0:
                folder_link = a[0].get("href")

            folder2url[folder] = folder_link

            if folder is not None:
                active_folder = folder
                folder2submenu_urls[active_folder] = []
            else:
                href = li.select("a")[0].get("href")
                folder2submenu_urls[active_folder].append(href)
        return folder2submenu_urls, folder2url


    @staticmethod
    def find_links_on_selected_menu(html):
        """ Returns a list of links to concrete articles """
        soup = BeautifulSoup(html)
        links = []

        # find two 'Hero' links at the top
        section_two_up = soup.select("section.c-two-up")
        if len(section_two_up) > 0:
            section_two_up = section_two_up[0]
            headlines = section_two_up.select(".c-entry-box-base__headline")
            for h in headlines:
                a = h.select("a")
                if len(a) > 0:
                    links.append(a[0].get("href"))

        # parsing the rest of the page (long scroll-list of the articles)
        r = soup.select("div.l-segment.l-main-content "
                        "div.c-compact-river__entry "
                        "a.c-entry-box--compact__image-wrapper")
        for a in r:
            links.append(a.get("href"))
        return links


    @staticmethod
    def parse_article_page(html):
        soup = BeautifulSoup(html)
        header_wrap = soup.select("article.l-main-content "
                                  "div.c-entry-hero__header-wrap")

        # if len(header_wrap) == 0:
        #     raise RuntimeError("no item found")

        article = ArticleResult()
        if len(header_wrap) == 0:
            article.parsing_error = "element {article.l-main-content div.c-entry-hero__header-wrap} was not found"
            return article

        header_text = header_wrap[0].select("h1")[0].text
        summary_text = soup.select("article.l-main-content p.c-entry-summary")[0].text
        authors_and_time = soup.select("article.l-main-content div.c-byline")[0].text
        authors_and_time = authors_and_time.replace("\n", "")
        authors_and_time = re.sub("\s{2,}", " ", authors_and_time).strip()

        times = soup.select("time")
        time = ""
        if len(times) > 0:
            time = times[0].get("datetime")

        # parsing tags:
        tags = soup.select("div.c-entry-group-labels "
                            "li.c-entry-group-labels__item "
                            "span")
        tags = [x.text.replace("\n", "") for x in tags]

        # article's content - select all p and h2 where the main text resides
        entry_content = soup.select("div.c-entry-content")
        main_text_tags = entry_content[0].select("h2, p[id]")
        main_text = ""
        for t in main_text_tags:
            main_text += t.text

        # References inside the article:
        refs = entry_content[0].select("a")

        article.tags = tags
        article.header = header_text
        article.summary = summary_text
        article.time = time
        article.byline = authors_and_time
        article.main_text = main_text
        article.inner_links = refs
        return article



