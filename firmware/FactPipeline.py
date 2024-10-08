from scrapy.exceptions import DropItem
from scrapy.http import Request

import hashlib
import urllib.parse
import urllib.request, urllib.parse, urllib.error
from itemadapter import ItemAdapter
import logging
from requests_toolbelt import sessions
import base64
import io
import json
import tarfile

from retry_requests import retry as retryrequests
from retry import retry
logger = logging.getLogger(__name__)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
from scrapy.utils.defer import maybe_deferred_to_future


class FactPipeline:
    def __init__(self, fact_url, fact_api_key = None):
        self.files_urls_field = 'file_urls'
        self.fact_url = fact_url
        self.session = sessions.BaseUrlSession(base_url=self.fact_url)
        if fact_api_key is not None:
            self.session.headers.update({
                'Authorization': fact_api_key
            })
        self.plugins = list(json.loads(self.session.get("status").text)['plugins'].keys())
        # Remove time consuming plugins
        try:
            self.plugins = [ p for p in self.plugins if p not in 
                            ["cwe_checker", "cwe_checker78", "ipc_analyzer", "tlsh"
                                                                  ,"file_system_metadata"]]
        except ValueError:
            pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            fact_url=crawler.settings.get('FACT_URL'),
            fact_api_key=crawler.settings.get('FACT_API_KEY', None)
        )
    # overrides function from FilesPipeline
    def get_media_requests(self, item):
        # check for mandatory fields
        for x in ["vendor", "url"]:
            if x not in item:
                raise DropItem(
                    "Missing required field '%s' for item: " % x)

        # resolve dynamic redirects in urls
        for x in ["mib", "sdk", "url"]:
            if x in item:
                split = urllib.parse.urlsplit(item[x])
                # remove username/password if only one provided
                if split.username or split.password and not (split.username and split.password):
                    item[x] =urllib.parse.urlunsplit(
                        (split[0], split[1][split[1].find("@") + 1:], split[2], split[3], split[4]))

                if split.scheme == "http":
                    item[x] = urllib.request.urlopen(item[x]).geturl()

        # check for filtered url types in path
        url = urllib.parse.urlparse(item["url"])
        # a special exception for the foscam html URL
        if 'foscam.com' in str(url.netloc):
            pass
        elif any(url.path.endswith(x) for x in [".pdf", ".php", ".txt", ".doc", ".rtf", ".docx", ".htm", ".html", ".md5", ".sha1", ".torrent"]):
            raise DropItem("Filtered path extension: %s" % url.path)
        elif any(x in url.path for x in ["driver", "utility", "install", "wizard", "gpl", "login"]):
            raise DropItem("Filtered path type: %s" % url.path)

        # generate list of url's to download
        item[self.files_urls_field] = [item[x]
                                       for x in ["mib", "url"] if x in item]
        
        # debug the download link
        ##############################
        #for link in item[self.files_urls_field]:
        #    logging.debug(link)


        # pass vendor so we can generate the correct file path and name
        return [Request(x, meta={"ftp_user": "anonymous", "ftp_password": "chrome@example.com", "vendor": item["vendor"]})
                for x in item[self.files_urls_field]]

    @staticmethod
    def calc_fact_uid(file):
        if file is None:
            return None
        chksum = hashlib.sha256(file).hexdigest()
        length = len(file)
        return f"{chksum}_{length}"

    @retry(tries=3, delay=1, backoff=2)
    @staticmethod
    def get(url):
        return retryrequests().get(url)

    # overrides function from FilesPipeline
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        files = self.get_media_requests(item)
        responses = []
        for f in files:
            resp = FactPipeline.get(f.url)
                
            if resp.ok:
                responses.append(resp)
            else:
                print("download unsuccesful {resp}")
        
        file_name = item.get("file_name", item["url"].split('/')[-1])

        if len(responses) == 1:
            binary = responses[0].content
        else:
            print("multiple files detected")
            # make tar with all files inmemory
            fileobj = io.BytesIO()
            tar = tarfile.open(fileobj=fileobj, mode="w")
            for response in responses:
                tarinfo = tarfile.TarInfo(response.url.split('/')[-1])
                tarinfo.size = len(response.body)
                tar.addfile(tarinfo, io.BytesIO(response.body))
            binary = fileobj.getvalue()
            file_name += ".tar"

        
        fact_uid = FactPipeline.calc_fact_uid(binary)

        if self.session.head("firmware/" + fact_uid).status_code == 400:
            params = {
                'binary': base64.b64encode(binary).decode(),
                'device_class': item.get('device_class', 'camera'),
                'device_name': item.get("product", None),
                'device_part': "complete",
                'file_name': file_name,
                'release_date': item.get("date", None),
                'requested_analysis_systems': self.plugins,
                'tags': 'scraper',
                'vendor': item['vendor'],
                'version': item.get("version", item.get("build", "v1"))
            }
            response = self.session.put("firmware", json=params)
            if response.ok:
                logger.info("Successfully uploaded %s", item["url"])
            else:
                logger.error("Failed to upload %s because %s", item["url"], response.text[:100])
        else:
            logger.info("%s was already in FACT", item["url"])

        return item
