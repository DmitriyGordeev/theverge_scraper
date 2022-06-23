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
from db_interface import DBInterface, Topic
import datetime


class Scraper:
    def __init__(self):
        self.root_domain = "https://theverge.com/"
        self.main_menu_folder2hrefs = dict()
        self.main_menu_folder2url = dict()
        self.folder2articles = dict()       # this will store
                                            # (folder e.g. 'tech') -> (list of urls of all articles)

        # TODO: 'look up to date' -  field
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        self.driver = webdriver.Chrome('drivers/chromedriver.exe', options=option)
        self.db_interface = DBInterface()

        # These are to be set after looking into Database with SELECT request: (?)
        self.last_article_time = datetime.datetime.today()
        self.db_existing_articles_urls = []

        self.from_scratch_mode = False
        self.max_pages_depth = 1


    def get_page_selenium(self, url: str) -> str:
        """ Gets page using selenium, extracts rendered html code of this entire page
        and returns as a string """
        self.driver.get(url)
        sleep(5)
        html = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        return html



    def requests_pipeline(self):
        self.from_scratch_mode = DBInterface.local_test__get_num_existing_articles_from_db() == 0
        self.last_article_time = DBInterface.local_test__get_the_last_article_time()

        self.find_main_menu_links()

        # if we haven't found any, just stop and log it
        if len(self.main_menu_folder2hrefs) == 0:
            print ("No menu links found")
            # TODO: logger
            exit(0)

        if self.from_scratch_mode:
            # loop through all main menu links and scrape all articles
            for folder in self.main_menu_folder2hrefs.keys():
                print (f"SCRAPING FOLDER = {folder}")
                self.find_new_articles_for_folder(folder)
                self.full_loop_through_folder_pages(f"/{folder}/archives", folder)

            # Loop through article urls in each folder:
            self.loop_through_gathered_articles()

        # if self.from_scratch_mode = False we search for new articles only
        # in this case we should have valid 'self.last_article_time'
        else:
            for folder in self.main_menu_folder2hrefs.keys():
                print (f"SCRAPING FOLDER = {folder}")
                self.find_new_articles_for_folder(folder)


    def find_main_menu_links(self):
        root = "https://theverge.com"
        html = requests.get(root, headers=self.emulate_headers()).text
        self.main_menu_folder2hrefs, self.main_menu_folder2url = Parser.parse_main_menu_links(html)

        # TODO: compare the database and check for new topics or prepare cache for switching old topics
        #  to inactive state when topics will be uploading to the database


    def full_loop_through_folder_pages(self, folder_page1_url, folder_name):
        # 1. получаем через selenium
        # 2. парсим все ссылки с помощью .find_links_on_selected_menu
        # 3. добавляем в дикт всех (tech -> конкретные ссылки)
        # 4. ищем кнопку next
        # 5. если найдена то берем след. страницу с selenium запускаем цикл
        f = open(f"{folder_name}_articles.log", "w")

        Path(f"{folder_name}").mkdir(parents=True, exist_ok=True)

        next_button_exists = True
        target_page = folder_page1_url
        num_pages_looked_through_so_far = 0
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

            print (f"target_page = {target_page}, num articles gathered = {len(article_links)}")

            # looking for 'next' button:
            soup = BeautifulSoup(page_html)
            hrefs = soup.select("a.c-pagination__next.c-pagination__link.p-button")
            if len(hrefs) == 0:
                print ("Next button was not found, break here")
                next_button_exists = False
                continue

            target_page = hrefs[0].get("href")

            num_pages_looked_through_so_far += 1
            if num_pages_looked_through_so_far >= self.max_pages_depth:
                print ("Max depth reached. Stop")
                return

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
                with open(folder + f"/{article_result_object.short()}.txt", "w") as f:
                    f.write(article_result_object.formatted_text())


    def find_new_articles_for_folder(self, folder_name):
        Path(f"{folder_name}").mkdir(parents=True, exist_ok=True)

        headers = self.emulate_headers()
        page_html = requests.get(self.root_domain + self.main_menu_folder2url[folder_name], headers=headers).text
        page_html = page_html.replace(">", ">\n")

        # parse all the refs to the concrete articles:
        article_links = Parser.find_links_on_selected_menu(page_html)
        count = 0
        for i, a_url in enumerate(article_links):
            count += 1
            print(f"parsing articles: {i}/{len(article_links)}")
            headers = self.emulate_headers()
            html_text = requests.get(a_url, headers=headers).text
            html_text = html_text.replace(">", ">\n")

            article_result = Parser.parse_article_page(html_text)
            article_result.url = a_url

            if article_result.parsing_error != "":
                continue

            print (f"title = {article_result.header}, article_result.time = {article_result.time}")

            current_article_datetime = datetime.datetime.strptime(article_result.time, "%Y-%m-%dT%H:%M:%S")

            # TODO: also we can retrieve urls for the past 5 days and find if current url is there
            #   if so we stop as well
            if current_article_datetime <= self.last_article_time:
                print ("Found old article, stop here")
                print (f"Num articles gathered = {count - 1}")
                return

            with open(folder_name + f"/{article_result.short()}.txt", "w") as f:
                f.write(article_result.formatted_text())



    def compare_topics_with_db(self):
        db_topics = DBInterface.local_test__get_exisiting_topics_from_db()
        db_topic_names = [x.topic for x in db_topics]
        scraped_topics = list(self.main_menu_folder2hrefs.keys())

        for i in range(len(db_topics)):
            if db_topics[i].topic not in scraped_topics:     # site doesn't have this topic now
                db_topics[i].active = False

        new_topics = []
        for st in scraped_topics:
            if st not in db_topic_names:      # we found brand new topic, need to add
                new_topics.append(st)

        # write into file json file for further work with database
        out_json = dict()
        out_json["new_topics"] = []
        out_json["inactive"] = []

        # Saving new topics into resulting json to be dumped
        # and caught by Database writer script
        for nt in new_topics:
            topic = Topic()
            topic.topic_id = 0
            topic.topic = nt
            url = self.main_menu_folder2url[nt]
            if url[0] == '/':
                topic.url = self.root_domain + url
            else:
                topic.url = url
            topic.active = True
            topic.news_source = "theverge"
            out_json["new_topics"].append(topic.to_dict())

        # Saving topics that should be deactivated (inactive set to False)
        for dbt in db_topics:
            if not dbt.active:
                out_json["inactive"].append(dbt.to_dict())

        with open("topics_update.json", "w") as f:
            f.write(json.dumps(out_json, indent=4))



    @staticmethod
    def emulate_headers():
        return ({'User-Agent':
                 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                 'Accept-Language': 'en-US, en;q=0.5'})