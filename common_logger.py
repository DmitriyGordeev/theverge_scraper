import logging
import datetime

def setup_logging_setting(filename):
    FORMAT = "[%(filename)s:%(lineno)s %(funcName)1s()] %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT, filename=filename)
    logging.getLogger().addHandler(logging.StreamHandler())