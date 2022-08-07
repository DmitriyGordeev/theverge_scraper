from scraper import *
import common_logger


def main():
    theVergeScraper = Scraper()
    theVergeScraper.requests_pipeline()


if __name__ == "__main__":

    # TODO: Settings.global_path + log_file_basename

    log_file_prefix = datetime.datetime.today().strftime("%Y-%m-%d_%Hh%Mm%Ss")
    log_file_basename = f"{log_file_prefix}_run_scrape_topics.log"
    common_logger.setup_logging_setting(log_file_basename)
    main()