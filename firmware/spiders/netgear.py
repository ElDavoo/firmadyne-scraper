import json

from scrapy import Spider, Request
from scrapy.http import FormRequest

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urllib.request, urllib.parse, urllib.error


class NetgearSpider(Spider):
    name = "netgear"
    allowed_domains = ["netgear.com"]
    # "http://downloadcenter.netgear.com/fr/", "http://downloadcenter.netgear.com/de/", "http://downloadcenter.netgear.com/it/", "http://downloadcenter.netgear.com/ru/", "http://downloadcenter.netgear.com/other/"]
    start_urls = ["https://www.netgear.com:443/system/supportModels.json"]
    download_path = "https://www.netgear.com:443/"

    # visited = []
    #
    # # grab the first argument from e.g.
    # # javascript:__doPostBack('ctl00$ctl00$ctl00$mainContent$localizedContent$bodyCenter$BasicSearchPanel$btnAdvancedSearch','')
    # @staticmethod
    # def strip_js(url):
    #     return url.split('\'')[1]

    def parse(self, response):
        json_response = json.loads(response.text)

        for model in json_response:
            if 'url' in model and 'model' in model and 'No-NETGEAR-support' not in model['url']:
                model_name = model['model']
                url = str(model['url'])

                if url.startswith("/"):
                    url = urllib.parse.urljoin(self.download_path, url)

                yield Request(
                    url=url,
                    headers={"Referer": response.url},
                    meta={"product": model_name},
                    callback=self.parse_model_page)

    def parse_model_page(self, response):
        for entry in response.xpath("//section[@id='topicsdownload']//div[@class='col topic']/"
                                    "section[@class='box articles']//div[@class='accordion-item']"):
            name = entry.xpath("./a[@class='accordion-title']/h1/text()").extract_first()
            url = entry.xpath("./div[@class='accordion-content']//a/@href").extract_first()

            if '#confirm-download-' in url or 'http://kb.netgear.com/' in url:
                continue

            if 'Firmware' in name and not 'Upgrade' in name:
                name_split = name.split(" ")
                index = name_split.index('Version')
                # only continue if there is a version number
                if index:
                    version = name_split[index+1]

                    item = FirmwareLoader(item=FirmwareImage(), response=response)
                    item.add_value("version", version)
                    item.add_value("url", url)
                    item.add_value("product", response.meta["product"])
                    item.add_value("vendor", self.name)
                    yield item.load_item()
