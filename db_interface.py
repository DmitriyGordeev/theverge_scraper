

class Topic:
    def __init__(self):
        self.topic_id = 0
        self.topic = ''
        self.url = ''
        self.news_source = ''
        self.active = False



class DBInterface:
    def __init__(self):
        pass


    def get_exisiting_topics_from_db(self):
        # TODO: should SELECT from db
        pass

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
        return out
