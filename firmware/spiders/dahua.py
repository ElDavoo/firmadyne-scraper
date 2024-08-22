from scrapy import Spider
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.loader.processors import MapCompose
from scrapy.loader.processors import Join
from scrapy.loader.processors import Identity

import json
import urllib.request, urllib.parse, urllib.error

class DahuaSpider(Spider):
    name = "dahua"
    allowed_domains = ["dahuasecurity.com"]
    start_urls = ["http://www.dahuasecurity.com/download_1.html"]

    custom_settings = {"CONCURRENT_REQUESTS": 3}

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True)

    def parse(self, response):
        for entry in response.xpath("//div[@class='down_list']/ul/li/a"):
            yield Request(
                url=urllib.parse.urljoin(response.url, entry.xpath("./@href").extract()[0]),
                headers={"Referer": response.url},
                meta={"product": entry.xpath("./text()").extract()[0]},
                callback=self.parse_product)

    def parse_product(self, response):
        for entry in response.xpath("//div[@class='down_list']/ul/li/a"):
            yield Request(
                url=urllib.parse.urljoin(response.url, entry.xpath("./@href").extract()[0]),
                headers={"Referer": response.url},
                meta={"product": response.meta["product"], "version": entry.xpath("./text()").extract()[0]},
                callback=self.parse_json)

    def parse_json(self, response):
        json_response = json.loads(response.body_as_unicode())

        for entry in json_response:
            item = ItemLoader(item=FirmwareImage(), response=response)
            item.default_output_processor = TakeFirst()

            item.add_value("version", response.meta["version"])
            item.add_value("description", entry["name"])
            item.add_value("url", urllib.parse.urljoin(response.url, entry["url"]))

            yield item.load_item()