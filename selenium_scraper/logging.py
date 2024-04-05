import logging
import sys

logging.getLogger('scrapy').propagate = False

logger = logging.getLogger("phone_scrapper")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('parser_logs.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(stdout_handler)
logger.addHandler(file_handler)


