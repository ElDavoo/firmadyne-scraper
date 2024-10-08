#coding:utf-8
from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

class A360Spider(Spider):
    name = "360Routers"
    allowed_domains = ["luyou.360.cn", "luyou.dl.qihucdn.com"]
    start_urls = ["http://luyou.360.cn/resource/js/common_info.js"]

    def parse(self, response):
        js = response.text
        if js.startswith("var commonInfo"):

            p_product = "id:\"(?P<product>.*?)\""
            p_description = "title:\"(?P<description>.*?)\""
            p_version = "romVersions:\"(?P<version>.*?)\""
            p_url = "romUrl:\"(?P<url>.*?)\""
            p_date = "updateDate:\"(?P<date>.*?)\""

            import re
            products = re.findall(p_product, js)
            descriptions = re.findall(p_description, js)
            versions = re.findall(p_version, js)
            urls = re.findall(p_url, js)
            dates = re.findall(p_date, js)

            for i in range(len(products)):
                product = products[i]
                url = urls[i]
                version = versions[i]
                description = descriptions[i]
                date = dates[i]

                item = FirmwareLoader(
                            item=FirmwareImage(), response=response)
                item.add_value("url", url)
                item.add_value("version", version)
                item.add_value("product", product)
                item.add_value("description", description)
                item.add_value("date", date)
                item.add_value("vendor", self.name)
                item.add_value("device_class", "router")
                yield item.load_item()
