import unittest
import db_interface
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

        for x in result:
            print(x)
