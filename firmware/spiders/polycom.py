from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urllib.request, urllib.parse, urllib.error


class PolycomSpider(Spider):
    name = "polycom"
    allowed_domains = ["polycom.com"]
    start_urls = ["https://support.polycom.com/content/support/north-america/usa/en/support/video.html",
                  "https://support.polycom.com/content/support/north-america/usa/en/support/network.html",
                  "https://support.polycom.com/content/support/north-america/usa/en/support/voice.html",]

    download = ""

    @staticmethod
    def fix_url(url):
        if "://" not in url:
            return PolycomSpider.download + url
        return url

    def parse(self, response):
        if "product" in response.meta:
            for entry in response.xpath("//div[@class='tab-content']//tr")[1:]:

                version = entry.xpath("./td[1]//a//text()").extract_first()
                url = entry.xpath("./td[2]//a/@href").extract_first()
                if version is None or url is None:
                    continue

                # remove unnecessary files
                to_remove_list = ["end user license agreement", "eula", "release notes",
                                                   "mac os", "windows", "guide", "(pdf)", "sample", "client",
                                                   "manager", "software", "virtual", "control_panel",
                                                   "activexbypass"]
                if any(x in url.lower() for x in to_remove_list) \
                        or any(x in version.lower() for x in to_remove_list) \
                        or any(url.endswith(x) for x in ["htm", "html", "pdf", "ova", ".plcm.vc"]):
                    continue

                url = urllib.parse.urljoin(
                            response.url, PolycomSpider.fix_url(url)),

                item = FirmwareLoader(
                    item=FirmwareImage(), response=response)
                item.add_value("version", version)
                item.add_value("url", url)
                item.add_value("product", response.meta["product"])
                item.add_value("vendor", self.name)
                yield item.load_item()

        # all entries on the product overview pages
        elif response.xpath("//div[@class='product-listing']") and "product" not in response.meta:
            for entry in response.xpath("//div[@class='product-listing']//li"):
                if not entry.xpath("./a"):
                    continue

                text = entry.xpath("./a//text()").extract_first()
                href = entry.xpath("./a/@href").extract_first().strip()
                # date = entry.xpath("./span//text()").extract()

                if any(x in text.lower() for x in ["advisories", "support", "notices", "features"]) \
                        or href.endswith(".pdf"):
                    continue

                path = urllib.parse.urlparse(href).path
                if any(path.endswith(x) for x in [".htm", ".html"]) or "(html)" in text.lower():
                    yield Request(
                        url=urllib.parse.urljoin(
                            response.url, PolycomSpider.fix_url(href)),
                        meta={"product": text},
                        headers={"Referer": response.url},
                        callback=self.parse)
