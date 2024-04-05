import pandas as pd

import scrapy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapy_selenium import SeleniumRequest
from scrapy.exceptions import CloseSpider

from selenium_scraper.spiders.settings import custom_settings, PHONES_COUNT
import json
from selenium_scraper.logging import logger

class PhonesSpider(scrapy.Spider):
    name = 'phones'

    base_url = "https://www.ozon.ru"
    custom_settings = custom_settings
    phones_os = []
    def start_requests(self):
        url = "https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating"
        yield SeleniumRequest(url=url, callback=self.parse, wait_time=20,
                                  wait_until=EC.presence_of_element_located((By.ID, "ozonTagManagerApp")), priority=1)

    def parse(self, response, **kwargs):

        if len(self.phones_os) >= PHONES_COUNT:
            raise CloseSpider("100 phones scrapped")
        item_class = response.meta['item_class']
        items = response.xpath(f"//div[contains(@class,'widget-search-result-container')]/div/div[@class='{item_class}']")
        for item in items:

            url = item.xpath('.//a/@href').get()
            item_type = item.xpath(".//*[contains(text(), 'Тип')]/font/text()").get()
            if item_type == 'Смартфон':
                logger.info(f"Requesting {url}")
                yield SeleniumRequest(url=self.base_url + url, callback=self.parse_phone, wait_time=10,
                      wait_until=EC.presence_of_element_located((By.ID, "section-characteristics")), dont_filter=True, priority=2)
        logger.debug(f"Items in page: {len(items)}")
        next_page = response.xpath("//div[@data-widget='megaPaginator']/*[2]/*[1]/*[1]//div[text()='Дальше']/../../@href").get()
        if next_page:
            yield SeleniumRequest(url=self.base_url + next_page, callback=self.parse, wait_time=10,
                  wait_until=EC.presence_of_element_located((By.ID, "ozonTagManagerApp")), priority=1)

    def parse_phone(self, response):
        if len(self.phones_os) >= PHONES_COUNT:
            raise CloseSpider("100 phones scrapped")
        logger.info(f"Parsing phone {response.request.url}")
        phone_string = response.xpath(f"//div[@id='section-characteristics']//*[contains(text(), 'Версия')]/../../*[2]//text()").get()
        if not phone_string:
            return
        try:
            phone_os, phone_os_version = phone_string.split(' ')
            if '.' in phone_os_version:
                phone_os_version = phone_os_version.split('.')[0]
        except IndexError:
            return
        self.phones_os.append({"phone_os": phone_os, "phone_os_version": phone_os_version})



    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        logger.info(f"Total items scraped: {len(self.phones_os)}")

        df = pd.DataFrame(self.phones_os)
        phones_os = df.groupby(['phone_os', 'phone_os_version'], as_index=False).size().sort_values('size', ascending=False)

        with open("phones.txt", "w", encoding="utf-8") as f:
            for _, phone in phones_os.iterrows():
                f.write(f"{phone['phone_os']} {phone['phone_os_version']} - {phone['size']}\n\r")
