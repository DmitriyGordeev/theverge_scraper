import pandas
import json
from postgre_db_interface import *
from sqlalchemy import create_engine
import glob


if __name__ == "__main__":

    # Connect to db:
    params = PostgreDBInterface.config()
    connection = create_engine('postgresql://postgres:1234@localhost:5432/news')

    files = glob.glob("data/articles/*.json")
    data = pandas.DataFrame()
    for i,f in enumerate(files):
        print (f"{i} / {len(files)}")
        if "error-" in f:
            continue

        try:
            news_json = json.loads(open(f, 'r').read())
            data = data.append(news_json, ignore_index=True)
        except IOError as e:
            print (e)

    data = data.drop("parsing_error", axis=1)
    times = data['dt']
    data['dt'] = pandas.to_datetime(times, utc=True)
    # data['dt'] = data['dt'].astype(pandas.Timestamp)
    data.to_sql('news', connection, if_exists="append", index=False)










