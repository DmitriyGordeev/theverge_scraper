from html_parser import *
import json
from postgre_db_interface import *
from scraper import *
from settings import *
import common_logger


if __name__ == "__main__":
    log_file_prefix = datetime.datetime.today().strftime("%Y-%m-%d_%Hh%Mm%Ss")
    log_file_basename = f"{log_file_prefix}_run_scrape_articles.log"
    common_logger.setup_logging_setting(log_file_basename)

    f = open(Settings.global_path + "/topic2articles.json", "r")
    topics2articles = json.loads(f.read())
    f.close()

    scraper = Scraper()

    Path(scraper.root_output_dir).mkdir(parents=True, exist_ok=True)
    Path(scraper.root_output_dir + "/articles").mkdir(parents=True, exist_ok=True)
    Path(Settings.global_path + "/errors/").mkdir(parents=True, exist_ok=True)

    scraper.loop_through_articles(topics2articles)















