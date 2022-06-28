import unittest
from postgre_db_interface import *
import psycopg2
import pandas


class TestPostgreDBInterface(unittest.TestCase):

    def test_sql_select(self):
        pdb = PostgreDBInterface()
        print ("num existing articles = ", pdb.get_num_existing_articles_from_db())
        topics = pdb.get_topics_from_db()
        pass


    def test_select_with_db_interface_and_pandas(self):
        pdb = PostgreDBInterface()
        df = pandas.read_sql('SELECT * FROM topics', con=pdb.conn)
        print (df)


    def test_db_interface_get_topics_from_db(self):
        pdb = PostgreDBInterface()
        print (pdb.get_topics_from_db())



