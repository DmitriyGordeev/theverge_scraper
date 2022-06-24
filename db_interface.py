import datetime
import mysql.connector


class Topic:
    def __init__(self):
        self.topic_id = 0
        self.topic = ''
        self.url = ''
        self.news_source = ''
        self.active = False

    def from_query_result(self, query_result: tuple):
        if len(query_result) != 5:
            return False
        self.topic_id = query_result[0]
        self.topic = query_result[1]
        self.url = query_result[2]
        self.news_source = query_result[3]
        self.active = query_result[4]
        return True



    def to_dict(self):
        out = dict()
        out["topic_id"] = self.topic_id
        out["topic"] = self.topic
        out["url"] = self.url
        out["news_source"] = self.news_source
        out["active"] = self.active
        return out


class DBInterface:
    def __init__(self):
        # todo: read credentials from file or from system $PATH variable (?)
        self.db = mysql.connector.connect(
            host="localhost",
            user="admin",
            password="1234",
            database="news"
        )
        self.news_source = 'theverge'
        # TODO: check if failed to instanciate db connection!


    def get_exisiting_topics_from_db(self):
        cursor = self.db.cursor()
        cursor.execute(f"select * from topics where news_source = '{self.news_source}'")
        result = cursor.fetchall()
        topics = []
        for r in result:
            topic = Topic()
            if topic.from_query_result(r):
                topics.append(topic)
        return topics


    def get_num_existing_articles_from_db(self):
        """ Does SELECT request in order to find how many articles
        of this source are already in the database.
        """
        cursor = self.db.cursor()
        cursor.execute(f"select * from news where url like '%{self.news_source}%'")
        result = cursor.fetchall()
        return len(result)


    def get_the_last_article_time(self):
        """ Extracts datetime of the last article from DB as a string and
            converts into python's datetime object
         """
        # select *
        # from news LImit
        # 1
        cursor = self.db.cursor()
        cursor.execute(f"select * from news where url like '%{self.news_source}%'")
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



