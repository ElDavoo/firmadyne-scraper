from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader


class TendaSpider(Spider):
    name = "tenda"
    vendor = "tenda"

    allowed_domains = ['www.tendacn.com']
    start_urls = ["https://www.tendacn.com/en/service/download-cata-11.html"]

    def parse(self, response):
        for entry in response.xpath("//tr[@class='downtr js-row-detail ']"):
            dr_name = str(entry.xpath(".//td[@class='dr_name']/a/text()").extract_first()).split(" ")
            url = "https:" + str(entry.xpath(".//td[@class='dr_name']/a/@href").extract_first())
            date = entry.xpath(".//td[@class='dr_date hidden-xs']/text()").extract_first()

            product = dr_name[0]
            version = dr_name[2]

            yield Request(
                    url=url,
                    meta={"version": version, "product": product, "date": date},
                    headers={"Referer": response.url},
                    callback=self.download_item)

    def download_item(self, response):
        url = "https:" + str(response.xpath("//div[@class='downbtns']/a/@href").extract_first())
        item = FirmwareLoader(item=FirmwareImage(),
                              response=response,
                              date_fmt=["%Y-%m-%d"])
        item.add_value("url", url)
        item.add_value("version", response.meta["version"])
        item.add_value("date", response.meta["date"])
        item.add_value("product", response.meta["product"])
        item.add_value("vendor", self.name)
        yield item.load_item()
