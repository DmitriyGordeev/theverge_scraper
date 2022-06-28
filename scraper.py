import json
from pathlib import Path
from time import sleep
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from html_parser import Parser
from postgre_db_interface import *


class Scraper:
    def __init__(self):
        self.root_domain = "https://theverge.com/"
        self.root_output_dir = "data"
        # self.main_menu_topic2hrefs = dict()
        self.main_menu_topic2url = dict()
        self.topic2articles = dict()       # this will store
                                            # (topic e.g. 'tech') -> (list of urls of all articles)
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        self.driver = webdriver.Chrome('drivers/chromedriver.exe', options=option)
        self.db_interface = PostgreDBInterface()

        # These are to be set after looking into Database with SELECT request: (?)
        # self.last_article_time = datetime.datetime.today()
        self.db_existing_articles_urls = []

        # this is a dict key = 'topic name', value is topic_id
        # contains a map of topics that exist in DB already
        self.existing_topic2topic_id = dict()

        self.from_scratch_mode = False
        self.max_pages_depth = 1


    def get_page_selenium(self, url: str) -> str:
        """ Gets page using selenium, extracts rendered html code of this entire page
        and returns as a string """
        self.driver.get(url)
        # TODO: how to define if url was rendered already ? Retries ? driver.ready () ?
        sleep(5)
        html = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        return html


    def requests_pipeline(self):
        Path(self.root_output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.root_output_dir + "/articles").mkdir(parents=True, exist_ok=True)

        self.from_scratch_mode = self.db_interface.get_num_existing_articles_from_db() == 0
        # self.last_article_time = self.db_interface.get_the_last_article_time()

        self.find_main_menu_links()

        # if we haven't found any, just stop and log it
        if len(self.main_menu_topic2url) == 0:
            print ("No menu links found")
            # TODO: logger
            exit(0)

        self.write_topics_update_file()

        if self.from_scratch_mode:
            # loop through all main menu links and scrape all articles
            for topic in self.main_menu_topic2url.keys():
                print (f"Scraping topic = {topic}")
                self.find_new_articles_for_topic(topic)
                self.loop_through_topic_pages(f"/{topic}/archives", topic)

            # # Loop through article urls in each topic:
            # self.loop_through_gathered_articles()

        # if self.from_scratch_mode = False we search for new articles only
        # in this case we should have valid 'self.last_article_time'
        else:
            for topic in self.main_menu_topic2url.keys():
                print (f"Scraping topic = {topic}")
                self.find_new_articles_for_topic(topic)

        with open("topic2articles.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(self.topic2articles, indent=4))


    def find_main_menu_links(self):
        root = "https://theverge.com"
        html = requests.get(root, headers=self.emulate_headers()).text
        self.main_menu_topic2url = Parser.parse_main_menu_links(html)

        # TODO: compare the database and check for new topics or prepare cache for switching old topics
        #  to inactive state when topics will be uploading to the database


    def loop_through_topic_pages(self, topic_page1_url, topic_name):
        """ Loops through pages for selected topic and get urls to concrete articles """
        next_button_exists = True
        target_page = topic_page1_url
        num_pages_looked_through_so_far = 0
        while next_button_exists:
            page_html = self.get_page_selenium(self.root_domain + target_page)
            if page_html == "":
                print ("page_html is empty")
                # TODO: log this case
                exit(1)

            # parse all the refs to the concrete articles:
            article_links = Parser.find_links_on_selected_menu(page_html)
            if topic_name in self.topic2articles:
                self.topic2articles[topic_name] += article_links
            else:
                self.topic2articles[topic_name] = article_links

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


    # def loop_through_gathered_articles(self):
    #     if not self.topic2articles:
    #         print ("self.topic2articles is empty")
    #         # TODO: log this
    #         exit(1)
    #
    #     for topic_name, articles in self.topic2articles.items():
    #         if len(articles) == 0:
    #             print (f"topic_name {topic_name} doesn't contain articles")
    #             # todo: log this
    #             continue
    #
    #         for i, url in enumerate(articles):
    #             print (f"parsing articles: {i}/{len(articles)}")
    #
    #             headers = self.emulate_headers()
    #             html_text = requests.get(url, headers=headers).text
    #             html_text = html_text.replace(">", ">\n")
    #
    #             article_result = Parser.parse_article_page(html_text)
    #             article_result.url = url
    #             article_result.topic_name = topic_name
    #
    #             # assign topic id if it is existing topic:
    #             if topic_name in self.existing_topic2topic_id:
    #                 article_result.topic_id = \
    #                     self.existing_topic2topic_id[topic_name]
    #
    #             with open(self.root_output_dir + f"/articles/{article_result.short()}.json", "w") as f:
    #                 f.write(article_result.to_json_string())



    def loop_through_articles(self, topics2articles):
        last_article_datetime = self.db_interface.get_the_last_article_time()

        # extract topics and select only active
        db_active_topics = self.db_interface.get_topics_from_db()
        db_active_topics = db_active_topics[db_active_topics["active"]]

        # Looping through collected article urls and respective topic
        # loaded from json file:
        for topic, urls in topics2articles.items():
            selection = db_active_topics[db_active_topics["topic"] == topic]
            topic_id = -1
            if selection.shape[0] > 0:
                if selection.shape[0] > 1:
                    # TODO: warning - multiple duplicating topics with the same name!
                    # TODO: log this
                    pass
                topic_id = selection["topic_id"][0]
            elif selection.shape[0] == 0:
                # TODO: error - topic was not found
                # TODO: log this
                continue

            self.parse_articles(urls=urls,
                                topic=topic,
                                topic_id=topic_id,
                                last_time=last_article_datetime)


    def parse_articles(self,
                       urls: list,
                       topic: str,
                       topic_id: int,
                       last_time: datetime.datetime):
        """
        TODO:
        :param urls:
        :param topic:
        :param topic_id:
        :param last_time:
        :return:
        """
        for url in urls:
            headers = self.emulate_headers()
            html_text = requests.get(url, headers=headers).text
            html_text = html_text.replace(">", ">\n")

            article_result = Parser.parse_article_page(html_text)
            article_result.url = url
            article_result.topic_id = topic_id

            if last_time is not None:
                art_time = datetime.datetime.strptime(article_result.time, "%Y-%m-%dT%H:%M:%S")
                if art_time <= last_time:
                    print (f"article time {art_time} <= last_time {last_time} - found old article,"
                           f" stop looking further")
                    # TODO: log this
                    break

            with open(self.root_output_dir +
                      f"/articles/{article_result.short(prefix=topic + '-')}.json", "w") as f:
                f.write(article_result.to_json_string())



    def find_new_articles_for_topic(self, topic_name):
        headers = self.emulate_headers()
        page_html = requests.get(self.root_domain + self.main_menu_topic2url[topic_name],
                                 headers=headers).text
        page_html = page_html.replace(">", ">\n")

        # parse all the refs to the concrete articles:
        article_links = Parser.find_links_on_selected_menu(page_html)
        self.topic2articles[topic_name] = article_links
        print (f"{topic_name}: gathered {len(article_links)} articles")

        # count = 0
        # for i, a_url in enumerate(article_links):
        #     count += 1
        #     print(f"parsing articles: {i}/{len(article_links)}")
        #     headers = self.emulate_headers()
        #     html_text = requests.get(a_url, headers=headers).text
        #     html_text = html_text.replace(">", ">\n")
        #
        #     article_result = Parser.parse_article_page(html_text)
        #     article_result.url = a_url
        #     article_result.topic_name = topic_name
        #
        #     # assign topic id if it is existing topic:
        #     if topic_name in self.existing_topic2topic_id:
        #         article_result.topic_id = \
        #             self.existing_topic2topic_id[topic_name]
        #
        #     if article_result.parsing_error != "":
        #         continue
        #
        #     print (f"title = {article_result.header}, article_result.time = {article_result.time}")
        #
        #     current_article_datetime = datetime.datetime.strptime(article_result.time, "%Y-%m-%dT%H:%M:%S")
        #
        #     if self.last_article_time is not None:
        #         # TODO: also we can retrieve urls for the past 5 days and find if current url is there
        #         #   if so we stop as well
        #         if current_article_datetime <= self.last_article_time:
        #             print ("Found old article, stop here")
        #             print (f"Num articles gathered = {count - 1}")
        #             return
        #
        #     with open(self.root_output_dir + f"/articles/{article_result.short()}.json", "w") as f:
        #         f.write(article_result.to_json_string())


    def write_topics_update_file(self):
        # db_topics = MysqlDBInterface.local_test__get_exisiting_topics_from_db()
        db_topics = self.db_interface.get_topics_from_db()
        db_topic_names = [x.topic for x in db_topics]
        scraped_topics = list(self.main_menu_topic2url.keys())

        for i in range(len(db_topics)):
            self.existing_topic2topic_id[db_topics[i].topic] = db_topics[i].topic_id
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
            url = self.main_menu_topic2url[nt]
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

        with open(self.root_output_dir + "/topics_update.json", "w") as f:
            f.write(json.dumps(out_json, indent=4))


    @staticmethod
    def emulate_headers():
        return ({'User-Agent':
                 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                 'Accept-Language': 'en-US, en;q=0.5'})