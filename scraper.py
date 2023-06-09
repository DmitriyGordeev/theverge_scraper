import json
from pathlib import Path
from time import sleep
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from html_parser import Parser
from postgre_db_interface import *
import pytz
from dateutil.parser import parse
from settings import Settings
import logging


class Scraper:
    def __init__(self):
        self.source_domain = "theverge.com"
        self.root_url = "https://" + self.source_domain
        self.root_output_dir = Settings.global_path + "data/"
        self.main_menu_topic2url = dict()
        self.topic2articles = dict()        # this will store
                                            # (topic e.g. 'tech') -> (list of urls of all articles)
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        self.driver = webdriver.Chrome(Settings.global_path + 'drivers/chromedriver', options=option)
        self.db_interface = PostgreDBInterface(self.source_domain)

        # These are to be set after looking into Database with SELECT request: (?)
        # self.last_article_time = datetime.datetime.today()
        self.db_existing_articles_urls = []

        # this is a dict key = 'topic name', value is topic_id
        # contains a map of topics that exist in DB already
        self.existing_topic2topic_id = dict()
        self.from_scratch_mode = False
        self.max_pages_depth = 2

        logging.info(f"source_domain = {self.source_domain}")
        logging.info(f"root_url = {self.root_url}")
        logging.info(f"root_output_dir = {self.root_output_dir}")
        logging.info(f"max_pages_depth = {self.max_pages_depth}")



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
        logging.info(f"self.from_scratch_mode = {self.from_scratch_mode}")

        self.find_main_menu_links()

        # if we haven't found any, just stop and log it
        if len(self.main_menu_topic2url) == 0:
            logging.warning("No menu links found")
            exit(0)

        self.write_topics_update_file()

        if self.from_scratch_mode:
            # loop through all main menu links and scrape all articles
            for topic in self.main_menu_topic2url.keys():
                logging.info(f"topic = {topic}")
                self.find_new_articles_for_topic(topic)
                self.loop_through_topic_pages(f"/{topic}/archives", topic)

        # if self.from_scratch_mode = False we search for new articles only
        # in this case we should have valid 'self.last_article_time'
        else:
            for topic in self.main_menu_topic2url.keys():
                logging.info(f"topic = {topic}")
                self.find_new_articles_for_topic(topic)

        with open(Settings.global_path + "topic2articles.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(self.topic2articles, indent=4))


    def find_main_menu_links(self):
        html = requests.get(self.root_url, headers=self.emulate_headers()).text
        self.main_menu_topic2url = Parser.parse_main_menu_links(html)

        # remove links to other domains:
        copy_dict = dict()
        for topic, url in self.main_menu_topic2url.items():
            if "https://" not in url:
                copy_dict[topic] = url
        self.main_menu_topic2url = copy_dict


    def loop_through_topic_pages(self, topic_page1_url, topic_name):
        """ Loops through pages for selected topic and get urls to concrete articles """
        next_button_exists = True
        target_page = topic_page1_url
        num_pages_looked_through_so_far = 0
        while next_button_exists:
            page_html = self.get_page_selenium(self.root_url + target_page)
            if page_html == "":
                logging.warning("page_html is empty")
                exit(1)

            # parse all the refs to the concrete articles:
            article_links = Parser.find_links_on_selected_menu(page_html)
            if topic_name in self.topic2articles:
                self.topic2articles[topic_name] += article_links
            else:
                self.topic2articles[topic_name] = article_links

            logging.info(f"target_page = {target_page}, num articles gathered = {len(article_links)}")

            # looking for 'next' button:
            soup = BeautifulSoup(page_html, "html.parser")
            hrefs = soup.select("a.c-pagination__next.c-pagination__link.p-button")
            if len(hrefs) == 0:
                logging.info("Next button was not found, break here")
                next_button_exists = False
                continue

            # stop if we reached maximum depth
            target_page = hrefs[0].get("href")
            num_pages_looked_through_so_far += 1
            if num_pages_looked_through_so_far >= self.max_pages_depth > 0:
                logging.info("Max depth reached. Stop")
                return



    def loop_through_articles(self, topics2articles):
        last_article_datetime = self.db_interface.get_last_article_time()
        logging.debug("Time of the latest article in the database = {last_article_datetime}")

        # extract topics and select only active
        db_active_topics = self.db_interface.get_topics_from_db()

        logging.debug("======\n", db_active_topics, "\n======\n")

        db_active_topics = db_active_topics[db_active_topics["active"]]

        # Looping through collected article urls and respective topic
        # loaded from json file:
        for topic, urls in topics2articles.items():
            selection = db_active_topics[db_active_topics["topic"] == topic]
            topic_id = -1
            if selection.shape[0] > 0:
                if selection.shape[0] > 1:
                    logging.warning(f"Found duplicating topics in the database with name '{topic}'")

                topic_id = list(selection["topic_id"])[0]
            elif selection.shape[0] == 0:
                logging.error(f"topic '{topic}' was not found in the database, skipping article collection for this topic")
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
        Loop through urls of articles for specified topic (and respective topic_id)
        If article's time <= last_time stop. Writes down parsed articles into directory
        :param urls: list of articles of the current topic
        :param topic: current topic's name
        :param topic_id:
        :param last_time: datetime, last article's datetime in the database
        """
        for idx, url in enumerate(urls):
            logging.info(f"progress {idx}/{len(urls)}")
            # get html with get request
            headers = self.emulate_headers()
            html_text = requests.get(url, headers=headers).text
            html_text = html_text.replace(">", ">\n")

            # parse article -> ArticleResult object
            article_result = Parser.parse_article_page(html_text)
            article_result.url = url
            article_result.topic_id = topic_id

            # check if article object has parsing errors
            # if so, we write it to errors/ directory and continue
            if len(article_result.parsing_error) > 0:
                logging.error(f"parsing error")
                with open(f"{Settings.global_path}/errors/{article_result.short(prefix=topic + '-')}.json", "w") as f:
                    f.write(article_result.to_json_string())
                continue

            # Compare article's time with last_time from DB
            if last_time is not None and article_result.time is not None:
                try:
                    art_time = parse(article_result.time)
                    art_time = art_time.replace(tzinfo=pytz.UTC)
                    last_time = last_time.replace(tzinfo=pytz.UTC)
                    if art_time <= last_time:
                        logging.error(f"article time {art_time} <= last_time {last_time} - found old article,"
                                      f"stop looking further")
                        break
                except ValueError as e:
                    logging.error(f"error while parsing {article_result.time}")

            with open(self.root_output_dir + f"/articles/{article_result.short(prefix=topic + '-')}.json", "w") as f:
                f.write(article_result.to_json_string())



    def find_new_articles_for_topic(self, topic_name):
        headers = self.emulate_headers()
        page_html = requests.get(self.root_url + self.main_menu_topic2url[topic_name],
                                 headers=headers).text
        page_html = page_html.replace(">", ">\n")

        # parse all the refs to the concrete articles:
        article_links = Parser.find_links_on_selected_menu(page_html)
        self.topic2articles[topic_name] = article_links
        logging.info(f"{topic_name}: gathered {len(article_links)} articles")


    def write_topics_update_file(self):
        """
        TODO:
        :return:
        """
        db_topics = self.db_interface.get_topics_from_db()
        scraped_topics = list(self.main_menu_topic2url.keys())

        # find inactive topics and switch
        for i in range(db_topics.shape[0]):
            if db_topics.iloc[i, db_topics.columns.get_loc("topic")] not in scraped_topics:
                db_topics.iloc[i, db_topics.columns.get_loc("active")] = False

        new_topics = []
        for st in scraped_topics:
            if st not in list(db_topics["topic"]):      # we found brand new topic, need to add
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
                topic.url = self.root_url + url
            else:
                topic.url = url
            topic.active = True
            topic.news_source = self.source_domain
            out_json["new_topics"].append(topic.to_dict())

        # Saving topics that should be deactivated (inactive set to False)
        for idx, r in db_topics.iterrows():
            if not r["active"]:
                out_json["inactive"].append(dict(r))

        with open(self.root_output_dir + "/topics_update.json", "w") as f:
            f.write(json.dumps(out_json, indent=4))


    @staticmethod
    def emulate_headers():
        return ({'User-Agent':
                 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                 'Accept-Language': 'en-US, en;q=0.5'})