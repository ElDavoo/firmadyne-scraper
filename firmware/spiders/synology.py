from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import os
import urllib.request, urllib.parse, urllib.error


class SynologySpider(Spider):
    name = "synology"
    allowed_domains = ["synology.com"]
    start_urls = ["https://archive.synology.com/download/DSM/release",
                  "https://archive.synology.com/download/VSM/release/",
                  "https://archive.synology.com/download/VSF/release",
                  "https://archive.synology.com/download/SRM/release/",
                  "https://archive.synology.com/download/DSMUC/release"]

    def parse(self, response):
        for entry in response.xpath("//table/tr[position() > 3]"):
            if not entry.xpath("./td[2]/a"):
                continue

            text = entry.xpath("./td[2]/a//text()").extract()[0]
            href = entry.xpath("./td[2]/a/@href").extract()[0]
            date = entry.xpath("./td[3]//text()").extract()[0]

            # if "DSM" in response.url:
            if 'DSMUC' in response.url:
                software = 'DSMUC'
            elif 'DSM' in response.url:
                software = "DSM"
            elif 'VSM' in response.url:
                software = "VSM"
            elif "VSF" in response.url:
                software = "VSF"
            elif "SRM" in response.url:
                software = "SRM"
            else:
                continue  # should not happen :-)

            if href.endswith('/'):
                build = None
                version = response.meta.get(
                    "version", FirmwareLoader.find_version_period([text]))
                if not FirmwareLoader.find_version_period([text]):
                    build = text[0: -1]

                yield Request(
                    url=urllib.parse.urljoin(response.url, href),
                    headers={"Referer": response.url},
                    meta={"build": build, "version": version},
                    callback=self.parse)
            elif all(not href.lower().endswith(x) for x in [".txt", ".md5", ".torrent"]):
                product = None
                basename = os.path.splitext(text)[0].split("_")

                if software in basename:
                    if response.meta["build"] in basename:
                        basename.remove(response.meta["build"])
                    basename.remove(software)
                    product = " ".join(basename)
                else:
                    # usually "synology_x86_ds13_1504
                    product = basename[-2]

                item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt=["%d-%b-%Y"])
                item.add_value("build", response.meta["build"])
                item.add_value("version", response.meta["version"])
                if software == "DSM":
                    item.add_value("mib", "https://global.download.synology.com/download/Document/Software/"
                                          "DeveloperGuide/Firmware/DSM/All/enu/Synology_MIB_File.zip")
                item.add_value("url", href)
                item.add_value("date", date)
                item.add_value("product", product)
                item.add_value("vendor", self.name)
                yield item.load_item()
