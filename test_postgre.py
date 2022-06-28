import unittest
from configparser import ConfigParser
import psycopg2
import pandas


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



def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')



class TestPostgreRequest(unittest.TestCase):

    def test_simple_connect_and_request(self):
        conn = psycopg2.connect(
            host="localhost",
            database="news",
            user="postgres",
            password="1234")

        cur = conn.cursor()
        cur.execute("SELECT * FROM topics")
        data = cur.fetchall()
        print (data)


    def test_load_db_settings_from_ini_and_connect(self):
        conn = psycopg2.connect(
            host="localhost",
            database="news",
            user="postgres",
            password="1234")
        df = pandas.read_sql('SELECT * FROM topics', con=conn)
        print(df)


    def test_load_db_with_ini_file(self):
        params = config()
        conn = psycopg2.connect(**params)
        df = pandas.read_sql('SELECT * FROM topics', con=conn)
        print(df)