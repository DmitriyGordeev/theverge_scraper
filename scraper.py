import os
import re
import unittest
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
from html_parser import Parser
from selenium import webdriver
from time import sleep
from pathlib import Path


class Scraper:
    def __init__(self):
        self.root_domain = "https://theverge.com/"
        self.main_menu_folder2hrefs = dict()
        self.folder2articles = dict()       # this will store
                                            # (folder e.g. 'tech') -> (list of urls of all articles)

        # TODO: 'look up to date' -  field
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        self.driver = webdriver.Chrome('drivers/chromedriver.exe', options=option)


    def get_page_selenium(self, url: str) -> str:
        """ Gets page using selenium, extracts rendered html code of this entire page
        and returns as a string """
        self.driver.get(url)
        sleep(5)
        html = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        return html



    def requests_pipeline(self):
        self.find_main_menu_links()

        # if we haven't found any, just stop and log it
        if len(self.main_menu_folder2hrefs) == 0:
            print ("No menu links found")
            # TODO: logger
            exit(0)

        # loop through all main menu links and scrape all articles
        for folder in self.main_menu_folder2hrefs.keys():
            print (f"SCRAPING FOLDER = {folder}")
            self.loop_through_folder_news(f"/{folder}/archives", folder)
            break   # TODO: remove, this is only for test

        # Loop through article urls in each folder:
        self.loop_through_gathered_articles()


    def find_main_menu_links(self):
        root = "https://theverge.com"
        html = requests.get(root, headers=self.emulate_headers()).text
        self.main_menu_folder2hrefs = Parser.parse_main_menu_links(html)

        # TODO: compare the database and check for new topics or prepare cache for switching old topics
        #  to inactive state when topics will be uploading to the database


    def loop_through_folder_news(self, folder_page1_url, folder_name):
        # 1. получаем через selenium
        # 2. парсим все ссылки с помощью .find_links_on_selected_menu
        # 3. добавляем в дикт всех (tech -> конкретные ссылки)
        # 4. ищем кнопку next
        # 5. если найдена то берем след. страницу с selenium запускаем цикл
        f = open(f"{folder_name}_articles.log", "w")

        next_button_exists = True
        target_page = folder_page1_url
        while next_button_exists:
            page_html = self.get_page_selenium(self.root_domain + target_page)
            if page_html == "":
                print ("page_html is empty")
                # TODO: log this case
                exit(1)

            # parse all the refs to the concrete articles:
            article_links = Parser.find_links_on_selected_menu(page_html)
            if folder_name in self.folder2articles:
                self.folder2articles[folder_name] += article_links
            else:
                self.folder2articles[folder_name] = article_links

            for al in article_links:
                f.write(al + "\n")

            print (f"target_page = {target_page}, num articles gathered = {len(article_links)}")

            # looking for 'next' button:
            soup = BeautifulSoup(page_html)
            hrefs = soup.select("a.c-pagination__next.c-pagination__link.p-button")
            if len(hrefs) == 0:
                print ("Next button was not found, break here")
                next_button_exists = False
                continue

            target_page = hrefs[0].get("href")
        f.close()


    def loop_through_gathered_articles(self):
        if not self.folder2articles:
            print ("self.folder2articles is empty")
            # TODO: log this
            exit(1)

        for folder, articles in self.folder2articles.items():
            if len(articles) == 0:
                print (f"folder {folder} doesn't contain articles")
                # todo: log this
                continue

            Path(f"{folder}").mkdir(parents=True, exist_ok=True)

            for i, url in enumerate(articles):
                print (f"parsing articles: {i}/{len(articles)}")

                headers = self.emulate_headers()
                html_text = requests.get(url, headers=headers).text
                html_text = html_text.replace(">", ">\n")

                # TODO: check if already in the database or not
                article_result_object = Parser.parse_article_page(html_text)
                article_result_object.url = url
                with open(folder + f"/{i}.txt", "w") as f:
                    f.write(article_result_object.formatted_text())



    @staticmethod
    def emulate_headers():
        return ({'User-Agent':
                 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                 'Accept-Language': 'en-US, en;q=0.5'})