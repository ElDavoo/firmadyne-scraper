from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.pipelines.files import FilesPipeline

import os
import hashlib
import urllib.parse
import urllib.request, urllib.parse, urllib.error
import logging
import requests
import re
from requests_toolbelt import sessions
import base64
import json
logger = logging.getLogger(__name__)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)


class FactPipeline(FilesPipeline):
    def __init__(self, store_uri, download_func=None, settings=None):
        self.fact_url = None
        def chk(settings, s: str):
            if not settings or s not in settings or settings[s] == "":
                return False
            return True 
        if chk(settings, "FACT_URL"):
            self.fact_url = settings["FACT_URL"]
        self.session = sessions.BaseUrlSession(base_url=self.fact_url)
        if chk(settings, "FACT_API_KEY"):
            self.session.headers.update({
                'Authorization': settings["FACT_API_KEY"]
            })
        self.plugins = list(json.loads(self.session.get("status").text)['plugins'].keys())
        # Remove time consuming plugins
        try:
            self.plugins.remove("cwe_checker", "cwe_checker78", "ipc_analyzer")
        except ValueError:
            pass
        self.store_uri = settings["FILES_STORE"]
        super(FactPipeline, self).__init__(store_uri, download_func,settings)

    @classmethod
    def from_settings(cls, settings):
        store_uri = settings['FILES_STORE']
        cls.expires = settings.getint('FILES_EXPIRES')
        cls.files_urls_field = settings.get('FILES_URLS_FIELD')
        cls.files_result_field = settings.get('FILES_RESULT_FIELD')

        return cls(store_uri, settings=settings)

    # overrides function from FilesPipeline
    def file_path(self, request, response=None, info=None):
        extension = os.path.splitext(os.path.basename(
            urllib.parse.urlsplit(request.url).path))[1]
        return "%s/%s%s" % (request.meta["vendor"],
                            hashlib.sha1(request.url.encode("utf8")).hexdigest(), extension)

    # overrides function from FilesPipeline
    def get_media_requests(self, item, info):
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
                    item[x] = urllib.parse.urlunsplit(
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
        return [Request(x, meta={"ftp_user": "anonymous", "ftp_password": "chrome@example.com", "vendor": item["vendor"]}) for x in item[self.files_urls_field]]

    def calc_fact_uid(self, path: str):
        file = self.read_fw(path)
        if file is None:
            return None
        chksum = hashlib.sha256(file).hexdigest()
        length = len(file)
        return f"{chksum}_{length}"

    def read_fw(self, path):
        file = None
        pth = os.path.join(self.store_uri, path)
        with open(pth, 'rb') as f:
            file = f.read()
        return file


    # overrides function from FilesPipeline
    def item_completed(self, results, item, info):
        item[self.files_result_field] = []
        if isinstance(item, dict) or self.files_result_field in item.fields:
            item[self.files_result_field] = [x for ok, x in results if ok]

        if not self.fact_url:
            return item

        # create mapping between input URL fields and results for each
        # URL
        status = {}
        for ok, x in results:
            for y in ["mib", "url", "sdk"]:
                # verify URL's are the same after unquoting
                if ok and y in item and urllib.parse.unquote(item[y]) == urllib.parse.unquote(x["url"]):
                    status[y] = x
                elif y not in status:
                    status[y] = {"checksum": None, "path": None}

        if not status["url"]["path"]:
            logger.warning("Empty filename for image: %s!" % item)
            return item

        fact_uid = self.calc_fact_uid(status["url"]["path"])

        if self.session.head("firmware/" + fact_uid).status_code == 400:
            params = {
                'binary': base64.b64encode(self.read_fw(status["url"]["path"])).decode(),
                'device_class': item.get('device_class', 'camera'),
                'device_name': item.get("product", None),
                'device_part': "complete",
                'file_name': item["url"].split('/')[-1],
                'release_date': item.get("date", None),
                'requested_analysis_systems': self.plugins,
                'tags': 'scraper',
                'vendor': item['vendor'],
                'version': item.get("version", item.get("build", None))
            }
            response = self.session.put("firmware", json=params)
            logger.info(f"Uploaded {item["url"].split('/')[-1]} to FACT")


        # # attempt to find a matching product_id
        # cur.execute("SELECT id FROM product WHERE iid=%s AND product IS NOT DISTINCT FROM %s AND version IS NOT DISTINCT FROM %s AND build IS NOT DISTINCT FROM %s",
        #             (image_id, item.get("product", None), item.get("version", None), item.get("build", None)))
        # product_id = cur.fetchone()

        # if not product_id:
        #     cur.execute("INSERT INTO product (iid, url, mib_filename, mib_url, mib_hash, sdk_filename, sdk_url, sdk_hash, product, version, build, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
        #                 (image_id, item["url"], status["mib"]["path"], item.get("mib", None), status["mib"]["checksum"], status["sdk"]["path"], item.get("sdk", None), status["sdk"]["checksum"], item.get("product", None), item.get("version", None), item.get("build", None), item.get("date", None)))
        #     product_id = cur.fetchone()
        #     logger.info(
        #         "Inserted database entry for product: %d!" % product_id)
        # else:
        #     cur.execute("UPDATE product SET (iid, url, mib_filename, mib_url, mib_hash, sdk_filename, sdk_url, sdk_hash, product, version, build, date) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) WHERE id=%s",
        #                 (image_id, item["url"], status["mib"]["path"], item.get("mib", None), status["mib"]["checksum"], status["sdk"]["path"], item.get("sdk", None), status["sdk"]["checksum"], item.get("product", None), item.get("version", None), item.get("build", None), item.get("date", None), image_id))
        #     logger.info("Updated database entry for product: %d!" % product_id)

        # self.database.commit()
        return item
