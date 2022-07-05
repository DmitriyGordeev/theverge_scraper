import datetime
from topics import Topic
from configparser import ConfigParser
import psycopg2
from sqlalchemy import create_engine
import pandas


class PostgreDBInterface:
    def __init__(self):
        self.conn = None
        self.news_source = 'theverge'
        self.connect()


    @staticmethod
    def config(filename='postgre_config.ini', section='postgresql'):
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


    def connect(self):
        """ Connect to the PostgreSQL database server """
        conn = None
        try:
            # read connection parameters
            params = PostgreDBInterface.config()

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self.conn = psycopg2.connect(**params)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            exit(1)     # TODO: should we exit?
        finally:
            if conn is not None:
                self.conn.close()
                print('Database connection closed.')


    def get_topics_from_db(self):
        # TODO: connection via sqlalchemy
        connection = create_engine('postgresql://postgres:1234@localhost:5432/news')
        df = pandas.read_sql(f'SELECT * FROM topics WHERE news_source = \'{self.news_source}\'',
                             con=self.conn)
        return df


    def get_num_existing_articles_from_db(self):
        """ Does SELECT request in order to find how many articles
        of this source are already in the database.
        """
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM news WHERE url LIKE '%{self.news_source}%'")
        result = cursor.fetchall()
        return len(result)


    def get_the_last_article_time(self):
        """ Extracts datetime of the last article from DB as a string and
            converts into python's datetime object
         """
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM news WHERE url LIKE '%{self.news_source}%'")
        result = cursor.fetchall()
        if len(result) > 0:
            if len(result[0]) > 4:
                return result[0][3]
        return None


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



