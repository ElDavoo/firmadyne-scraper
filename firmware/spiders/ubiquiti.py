from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import json
import urllib.request, urllib.parse, urllib.error


class UbiquitiSpider(Spider):
    name = "ubiquiti"
    allowed_domains = ["ubnt.com", "ui.com"]
    start_urls = ["https://www.ui.com/download/airmax-ac",
                  "https://www.ui.com/download/unifi",
                  "https://www.ui.com/download/unifi-video",
                  "https://www.ui.com/download/airfiber",
                  "https://www.ui.com/download/ltu",
                  "https://www.ui.com/download/ufiber",
                  "https://www.ui.com/download/edgemax",
                  "https://www.ui.com/download/mfi",
                  "https://www.ui.com/download/sunmax"]

    def parse(self, response):
        for platform in response.xpath(
                "//a[@data-ga-category='download-nav']/@data-slug").extract():
            yield Request(
                url=urllib.parse.urljoin(response.url, "?group=%s" % (platform)),
                headers={"Referer": response.url,
                         "X-Requested-With": "XMLHttpRequest"},
                callback=self.parse_json)

    def parse_json(self, response):
        json_response = json.loads(response.body_as_unicode())

        if "products" in json_response:
            for product in json_response["products"]:
                yield Request(
                    url=urllib.parse.urljoin(
                        response.url, "?product=%s" % (product["slug"])),
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    meta={"product": product["slug"]},
                    callback=self.parse_json)

        if "url" in response.meta:
            print(response.meta["url"])
            item = FirmwareLoader(item=FirmwareImage(),
                                  response=response, date_fmt=["%Y-%m-%d"])
            item.add_value("url", response.meta["url"])
            item.add_value("product", response.meta["product"])
            item.add_value("date", response.meta["date"])
            item.add_value("description", response.meta["description"])
            item.add_value("build", response.meta["build"])
            item.add_value("version", response.meta["version"])
            item.add_value("sdk", json_response["download_url"])
            item.add_value("vendor", self.name)
            yield item.load_item()

        elif "product" in response.meta:
            for entry in json_response["downloads"]:
                if entry["category__slug"] == "firmware":

                    if entry["sdk__id"]:
                        yield Request(
                            url=urllib.parse.urljoin(
                                response.url, "?gpl=%s&eula=True" % (entry["sdk__id"])),
                            headers={"Referer": response.url,
                                     "X-Requested-With": "XMLHttpRequest"},
                            meta={"product": response.meta["product"], "date": entry["date_published"], "build": entry[
                                "build"], "url": entry["file_path"], "version": entry["version"], "description": entry["name"]},
                            callback=self.parse_json)
                    else:
                        url = entry["file_path"]
                        # print(url)
                        if url.startswith('/'):
                            url = urllib.parse.urljoin("http://www.ui.com/", url)
                        item = FirmwareLoader(
                            item=FirmwareImage(), response=response, date_fmt=["%Y-%m-%d"])
                        item.add_value("url", url)
                        item.add_value("product", response.meta["product"])
                        item.add_value("date", entry["date_published"])
                        item.add_value("description", entry["name"])
                        item.add_value("build", entry["build"])
                        item.add_value("version", entry["version"])
                        item.add_value("vendor", self.name)
                        yield item.load_item()
