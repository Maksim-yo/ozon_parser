# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import undetected_chromedriver as uc
from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By


class SeleniumUCMiddleware:
    def __init__(self):
        options = uc.ChromeOptions()
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        options.add_argument('--user-agent={0}'.format(user_agent))

        self.driver = uc.Chrome(headless=True, options=options)

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware

    def process_request(self, request, spider):
        if not isinstance(request, SeleniumRequest):
            return None
        self.driver.get(request.url)

        for cookie_name, cookie_value in request.cookies.items():
            self.driver.add_cookie(
                {
                    'name': cookie_name,
                    'value': cookie_value
                }
            )

        if request.wait_until:
            WebDriverWait(self.driver, request.wait_time).until(
                request.wait_until
            )

        if request.screenshot:
            request.meta['screenshot'] = self.driver.get_screenshot_as_png()

        if request.script:
            self.driver.execute_script(request.script)


        if "category" in request.url:
            self.driver.switch_to.default_content()
            self.driver.save_screenshot("screenshot.png")
            item_class = self.driver.find_elements(by=By.XPATH, value="//div[contains(@class,'widget-search-result-container')]/div/div[1]")[0].get_attribute('class')
            total_items = self.driver.find_elements(by=By.XPATH, value=f"//div[contains(@class,'widget-search-result-container')]/div/div")

            request.meta['item_class'] = item_class
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: items_count(driver, len(total_items), item_class))
            except TimeoutException:
                raise Exception("Page with items partial loaded")

        body = str.encode(self.driver.page_source)

        request.meta.update({'driver': self.driver})
        return HtmlResponse(
            self.driver.current_url,
            body=body,
            encoding='utf-8',
            request=request
        )

    def spider_closed(self):
        self.driver.quit()


def items_count(driver, min_len, item_class):
    return len(driver.find_elements(by=By.XPATH, value=f"//div[contains(@class,'widget-search-result-container')]/div/div[@class='{item_class}']")) >= min_len
