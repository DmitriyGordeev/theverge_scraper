import re
import unittest
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
import uuid


class Article:
    def __init__(self):
        self.url = ""
        self.tags = []
        self.header = ""
        self.summary = ""
        self.byline = ""
        self.time = ""
        self.main_text = ""
        self.inner_links = []
        self.parsing_error = []
        self.topic_id = 0


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
        out["topic_id"] = int(self.topic_id)
        if len(self.parsing_error) > 0:
            out["parsing_error"] = self.parsing_error
        return json.dumps(out, indent=4)


    def short(self, prefix=""):
        if self.header == "":
            return "error-" + uuid.uuid4().hex
        header = self.header.lower()
        header = re.sub('[^a-zA-Z ]+', '', header)
        words = header.split(" ")
        out = ''
        if len(words) > 2:
            out = '_'.join(words[:2])
        out = out + "_" + self.time
        out = out.replace(":", "")
        out = prefix + out
        return out


class Parser:
    @staticmethod
    def parse_main_menu_links(html):
        """ Returns a dict: key=topic, value=url """
        soup = BeautifulSoup(html, "html.parser")
        header_section_search_result = soup.select('section.c-nav-list')
        if len(header_section_search_result) == 0:
            raise ValueError("")

        header_section = header_section_search_result[0]
        r = header_section.select("li")

        # TODO: change assert to ..? !
        assert len(r) > 0

        folder2url  = dict()
        for li in r:
            folder = li.get("data-nav-item-id")
            if folder is None:
                continue
            a = li.select("a")
            folder_link = ""
            if len(a) > 0:
                folder_link = a[0].get("href")
            folder2url[folder] = folder_link
        return folder2url


    @staticmethod
    def find_links_on_selected_menu(html):
        """ Returns a list of links to concrete articles """
        soup = BeautifulSoup(html, "html.parser")
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
        soup = BeautifulSoup(html, "html.parser")
        header_wrap = soup.select("article.l-main-content "
                                  "div.c-entry-hero__header-wrap")

        article = Article()
        if len(header_wrap) == 0:
            article.parsing_error.append("Parsing header-wrap error: element {article.l-main-content div.c-entry-hero__header-wrap} was not found")
            return article

        header = header_wrap[0].select("h1")
        if len(header) > 0:
            header_text = header[0].text
            article.header = header_text
        else:
            article.parsing_error.append("Parsing header error: 'header_wrap[0].select(\"h1\")' is empty")

        summary = soup.select("article.l-main-content p.c-entry-summary")
        if len(summary) > 0:
            summary_text = summary[0].text
            article.summary = summary_text
        else:
            article.parsing_error.append("Parsing summary error: "
                                         "'soup.select('article.l-main-content p.c-entry-summary')' is empty")


        byline = soup.select("article.l-main-content div.c-byline")
        if len(byline) > 0:
            authors_and_time = byline[0].text
            authors_and_time = authors_and_time.replace("\n", "")
            authors_and_time = re.sub("\s{2,}", " ", authors_and_time).strip()
            article.byline = authors_and_time
        else:
            article.parsing_error.append("Parsing byline error: "
                                         "soup.select(\"article.l-main-content div.c-byline\") is empty")


        times = soup.select("time")
        if len(times) > 0:
            time = times[0].get("datetime")
            article.time = time
        else:
            article.parsing_error.append("Parsing byline error: "
                                         "soup.select(\"time\") is empty")

        # parsing tags:
        tags = soup.select("div.c-entry-group-labels "
                            "li.c-entry-group-labels__item "
                            "span")
        tags = [x.text.replace("\n", "") for x in tags]
        article.tags = tags

        # article's content - select all p and h2 where the main text resides
        entry_content = soup.select("div.c-entry-content")
        if len(entry_content) > 0:
            main_text_tags = entry_content[0].select("h2, p[id]")
            main_text = ""
            for t in main_text_tags:
                main_text += t.text
            article.main_text = main_text

        # References inside the article:
        refs = entry_content[0].select("a")
        article.inner_links = refs
        return article



