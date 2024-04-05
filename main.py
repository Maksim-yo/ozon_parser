import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from selenium_scraper.spiders.phones_spider import PhonesSpider

settings = get_project_settings()
parser = CrawlerProcess(settings)
parser.crawl(PhonesSpider)
parser.start()