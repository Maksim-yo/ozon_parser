import scrapy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapy_selenium import SeleniumRequest
from scrapy.exceptions import CloseSpider

from selenium_scraper.spiders.settings import custom_settings, PHONES_COUNT


class PhonesSpider(scrapy.Spider):
    name = 'phones'

    phone_count = 0
    base_url = "https://www.ozon.ru"
    custom_settings = custom_settings
    def start_requests(self):
        url = "https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating"
        yield SeleniumRequest(url=url, callback=self.parse, wait_time=20,
                                  wait_until=EC.presence_of_element_located((By.ID, "ozonTagManagerApp")), priority=1)

    def parse(self, response, **kwargs):

        if self.phone_count > PHONES_COUNT:
            raise CloseSpider("100 phones scrapped")
        item_class = response.meta['item_class']
        items = response.xpath(f"//div[contains(@class,'widget-search-result-container')]/div/div[@class='{item_class}']")
        for item in items:

            url = item.xpath('.//a/@href').get()
            item_type = item.xpath(".//*[contains(text(), 'Тип')]/font/text()").get()
            if item_type == 'Смартфон':
                yield SeleniumRequest(url=self.base_url + url, callback=self.parse_phone, wait_time=10,
                      wait_until=EC.presence_of_element_located((By.ID, "section-characteristics")), dont_filter=True, priority=2)

        next_page = response.xpath("//div[@data-widget='megaPaginator']/*[2]/*[1]/*[1]//div[text()='Дальше']/../../@href").get()
        if next_page:
            yield SeleniumRequest(url=self.base_url + next_page, callback=self.parse, wait_time=10,
                  wait_until=EC.presence_of_element_located((By.ID, "ozonTagManagerApp")), priority=1)

    def parse_phone(self, response):
        if self.phone_count > PHONES_COUNT:
            raise CloseSpider("100 phones scrapped")
        phone_string = response.xpath(f"//div[@id='section-characteristics']//*[contains(text(), 'Версия')]/../../*[2]//text()").get()
        if not phone_string:
            return
        try:
            phone_os, phone_os_version = phone_string.split(' ')
            if '.' in phone_os_version:
                phone_os_version = phone_os_version.split('.')[0]
        except IndexError:
            return
        self.phone_count += 1
        yield {"phone_os": phone_os, "phone_os_version": phone_os_version, "url": response.request.url}


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        spider.logger.info("Spider closed: %s", spider.name)
