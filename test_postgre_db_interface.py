import unittest
from postgre_db_interface import *
import psycopg2


class TestPostgreDBInterface(unittest.TestCase):

    def test_sql_select(self):
        pdb = PostgreDBInterface()
        print ("num existing articles = ", pdb.get_num_existing_articles_from_db())
        topics = pdb.get_exisiting_topics_from_db()
        pass



