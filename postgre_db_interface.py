import datetime
from topics import Topic
from configparser import ConfigParser
import psycopg2
from sqlalchemy import create_engine
import pandas
from settings import Settings


class PostgreDBInterface:
    def __init__(self, root_domain):
        self.news_source_domain = root_domain
        config = self.config()
        # connection example: postgresql://user:password@localhost:5432/database
        connection_argument = f'postgresql://{config["user"]}:{config["password"]}@{config["host"]}:5432/{config["database"]}'
        self.db_engine = create_engine(connection_argument)


    @staticmethod
    def config(filename=Settings.global_path + 'postgre_config.ini', section='postgresql'):
        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(filename)

        # get section, default to postgresql
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))
        return db


    def get_topics_from_db(self):
        with self.db_engine.connect() as connection:
            # TODO: log sql request
            df = pandas.read_sql(f'SELECT * FROM topics WHERE news_source = \'{self.news_source_domain}\'',
                                 con=connection)
            return df


    def get_num_existing_articles_from_db(self):
        """ Does SELECT request in order to find how many articles
        of this source are already in the database.
        """
        with self.db_engine.connect() as connection:
            df = pandas.read_sql(f'SELECT news_id FROM news WHERE url LIKE \'%%{self.news_source_domain}%%\'', con=connection)
            return df.shape[0]


    def get_last_article_time(self):
        """ Extracts datetime of the last article from DB as a string and
            converts into python's datetime object
         """
        with self.db_engine.connect() as connection:
            df = pandas.read_sql(f'SELECT dt FROM news WHERE url LIKE \'%%{self.news_source_domain}%%\'', con=connection)
            df = df.sort_values(by="dt")
            if df.shape[0] == 0:
                return None
            return df.iloc[-1][0]


    @staticmethod
    def local_test__get_the_last_article_time():
        test_datetime_extracted_from_db = "2022-06-21T23:00:00"
        out = datetime.datetime.strptime(test_datetime_extracted_from_db, "%Y-%m-%dT%H:%M:%S")
        return out


    @staticmethod
    def local_test__get_num_existing_articles_from_db():
        return 1


    @staticmethod
    def local_test__get_exisiting_topics_from_db():
        out = []
        t = Topic()
        t.topic_id = 1
        t.topic = "tech"
        t.url = "https://theverge.com/tech"
        t.news_source = "theverge"
        t.active = True
        out.append(t)

        t = Topic()
        t.topic_id = 2
        t.topic = "reviews"
        t.url = "https://theverge.com/reviews"
        t.news_source = "theverge"
        t.active = True
        out.append(t)

        t = Topic()
        t.topic_id = 4
        t.topic = "bionanolol"
        t.url = "https://theverge.com/bionanolol"
        t.news_source = "theverge"
        t.active = True
        out.append(t)

        return out



