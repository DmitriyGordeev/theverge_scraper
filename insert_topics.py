import pandas
import psycopg2
import json
from postgre_db_interface import *
from sqlalchemy import create_engine

""" Simple script to test intermediate insertion of scraped topics """

if __name__ == "__main__":

    # Connect to db:
    params = PostgreDBInterface.config()
    # connection = psycopg2.connect(**params)
    connection = create_engine('postgresql://postgres:1234@localhost:5432/news')

    with open("data/topics_update.json", "r") as f:
        topics_update = json.loads(f.read())

    new_topics = topics_update["new_topics"]
    inactive_topics = topics_update["inactive"]

    if len(new_topics) > 0:
        df = pandas.DataFrame()
        for nt in new_topics:
            if nt["active"] != 0:
                nt["active"] = True
            df = df.append(nt, ignore_index=True)

        df["active"] = df["active"].astype(bool)
        df = df.drop("topic_id", axis=1)
        df.to_sql('topics', connection, if_exists="append", index=False)


