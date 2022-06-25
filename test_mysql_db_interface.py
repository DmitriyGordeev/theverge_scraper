import unittest
import mysql_db_interface
import mysql.connector


class TestDBInterface(unittest.TestCase):

    def test_sql_select(self):
        mydb = mysql.connector.connect(
            host="localhost",
            user="admin",
            password="1234",
            database="news"
        )

        cursor = mydb.cursor()
        cursor.execute("select * from news where url like '%theverge%'")
        result = cursor.fetchall()
        print (len(result))
        for x in result:
            print(x)


    def test_get_topics(self):
        db = mysql_db_interface.MysqlDBInterface()
        r = db.get_exisiting_topics_from_db()
        pass


    def test_get_first(self):
        mydb = mysql.connector.connect(
            host="localhost",
            user="admin",
            password="1234",
            database="news"
        )

        cursor = mydb.cursor()
        news_source = 'theverge'
        cursor.execute(f"select * from news limit 1")
        result = cursor.fetchall()
        print (result)
