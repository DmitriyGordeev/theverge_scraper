import unittest
import re
import unittest
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
from html_parser import Parser

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait  # for implicit and explict waits
from selenium.webdriver.chrome.options import Options  # for suppressing the browser

from time import sleep


class TestSelenium(unittest.TestCase):

    def test_install_chromedriver(self):
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        driver = webdriver.Chrome('drivers/chromedriver.exe', options=option)

        driver.get('https://www.theverge.com/tech/archives')
        sleep(5)
        html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        with open("tech_archives.html", "w") as f:
            f.write(html)