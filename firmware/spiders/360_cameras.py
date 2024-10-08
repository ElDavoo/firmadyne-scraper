#coding:utf-8
from scrapy import Spider
from scrapy.http import Request
from firmware.selenium import SeleniumRequest
from selenium.webdriver.common.by import By

from firmware.items import FirmwareImage
from humanfriendly import parse_size
from firmware.loader import FirmwareLoader
from time import sleep
import dateutil.parser as dateparser
from selenium.common.exceptions import TimeoutException
from scrapy.downloadermiddlewares.retry import get_retry_request
# import webdriverwait
from selenium.webdriver.support.ui import WebDriverWait
import json
# set logging level of seleniumwire to ERROR
import logging
import re
logging.getLogger('seleniumwire').setLevel(logging.WARNING)
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

class A360Spider(Spider):
    name = "360Cameras"
    scopes = ['.*cjjd19.com']

    def start_requests(self):
        yield Request(
            url="https://bbs.360.cn/thread-15799665-1-1.html",
            callback=self.parse)

    def parse(self, response):

        td = response.xpath('//*[@id="postmessage_116541556"]')
        # Find the table inside it
        table = td.xpath('.//table')
        # Find the rows
        rows = table.xpath('.//tr')
        # Scheduling defect workaround (we don't want to open 16 ff drivers at once)
        # Nothing I tried works, so we just "manually" launch one single driver
        self.selrequests = []
        # Skip the first row
        for row in rows[1:]:
            # Find the columns
            cols = row.xpath('.//td')
            if len(cols) < 3:
                self.logger.warning("Expected at least 3 columns, got %d", len(cols))
                continue
            # Extract the data
            model = cols[1].xpath('.//text()').get()
            url = cols[2].xpath('.//a/@href').get()

            self.selrequests.append(SeleniumRequest(url=url, callback=self.parse_123pan,
                      meta={
                          "model": model,
                      },
                      capture_scopes=['.*cjjd19.com'],
                      priority=100,))
        yield self.get_next_request()
        #TODO There are other links after the table, we should get them too
    
    def get_next_request(self):
        if len(self.selrequests) > 0:
            return self.selrequests.pop(0)
        return None

    def parse_123pan(self, response):
        driver = response.meta['driver']
        del driver.requests
        driver.implicitly_wait(20)
        # Find the tbody ant-table-tbody
        tbody = driver.find_element(By.CLASS_NAME, "ant-table-tbody")
        # Find the not hidden rows (the ones that do not have aria-hidden)
        rows = tbody.find_elements(By.XPATH, "//tr[not(@aria-hidden)]")
        if len(rows) != 2:
            self.logger.warning("Expected 1 row, got %d", len(rows))
        date = None
        try:
            row = rows[1]
            # Find the columns
            cols = row.find_elements(By.TAG_NAME, "td")
            file_name = cols[1].text
            # Extract the date
            date = cols[3].text
            date = dateparser.parse(date)
            date = date.isoformat()
            size = cols[4].text
            size = parse_size(size)
            if size > 100 * 1024 * 1024:
                self.logger.warning("File is too big, 123pan requires an account: %s", size)
                driver.quit()
                yield self.get_next_request()
                return
        except Exception as e:
            self.logger.error("Error parsing date: %s", e)
            date = None

        # Find the series of three buttons in the right
        rightInfo = driver.find_element(By.CLASS_NAME, "rightInfo")
        # Take the first button and click it. It doesn't have a tag, so take the first child
        btn = rightInfo.find_elements(By.CLASS_NAME, "register")[0]
        # Block further requests
        driver.request_interceptor = lambda request: request.abort()
        btn.click()
        # Wait 10 seconds for request to be made. If doesn't happen, click again
        try:
            WebDriverWait(driver, 20).until(lambda driver: len(driver.requests) > 0)
        except Exception:
            request_or_none = get_retry_request(response.request,
                                    spider=self,
                                    reason="Download not started")
            driver.quit()
            if request_or_none:
                yield request_or_none
            else:
                yield self.get_next_request()
            return

        logging.info("Got the download link")

        yield Request(url=driver.last_request.url, callback=self.parse_redirectjson, meta={
            "driver": driver,
            "date": date,
            "model": response.meta['model'],
            "file_name": file_name
            }, priority=-1)

        # The middleware should do this
        driver.quit()
        # 
        # item = FirmwareLoader(
        #             item=FirmwareImage(), response=response)
        # item.add_value("url", url)
        # item.add_value("version", version)
        # item.add_value("product", product)
        # item.add_value("description", description)
        # item.add_value("date", date)
        # item.add_value("vendor", self.name)
        # item.add_value("device_class", "router")
        # yield item.load_item()
    def parse_redirectjson(self, response):
        # Extract the JSON from the response
        data = json.loads(response.text)
        # Extract the URL
        url = data["data"]["redirect_url"]
        item = FirmwareLoader(
            item=FirmwareImage(), response=response)
        item.add_value("url", url)
        item.add_value("vendor", "360")
        item.add_value("device_class", "camera")
        item.add_value("product", response.meta['model'])
        item.add_value("date", response.meta['date'])
        item.add_value("file_name", response.meta['file_name'])
        yield item.load_item()
        yield self.get_next_request()