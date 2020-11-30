from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urllib.request, urllib.parse, urllib.error


class FoscamSpider(Spider):
    name = "foscam"
    allowed_domains = ["foscam.com"]
    start_urls = [
        "http://www.foscam.com/downloads/firmware_details.html"]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, cookies={'loginEmail': "@.com"}, dont_filter=True)

    def parse(self, response):
        # bit ugly but it works :-)
        if "pid" not in response.meta:
            print("doei")
            for pid in range(0, 1000):
                yield Request(
                    url=urllib.parse.urljoin(response.url, "firmware_details.html?id=%s" % pid),
                    meta={"pid": pid},
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    callback=self.parse)
        else:
            for product in response.xpath("//div[@class='download_list_icon']/span/text()").extract():
                print(product)

                prods = response.xpath("//table[@class='down_table']//tr")
                # print(prods)
                # skip the table header
                for p in [x for x in prods[1:]]:
                    print('ey')
                    print(p.xpath('td[6]//a/@href').extract())
                    item = FirmwareLoader(item=FirmwareImage(), response=response)
                    item.add_value("version", p.xpath('td[1]//text()').extract())
                    item.add_value("url", 'https://foscam.com' + p.xpath('td[6]//a/@href').extract_first())
                    item.add_value("product", product)
                    item.add_value("vendor", self.name)
                    yield item.load_item()
