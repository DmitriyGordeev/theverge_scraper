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