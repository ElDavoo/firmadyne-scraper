BOT_NAME = "firmware"

SPIDER_MODULES = ["firmware.spiders"]
NEWSPIDER_MODULE = "firmware.spiders"

# https://docs.scrapy.org/en/latest/topics/settings.html#download-handlers
DOWNLOAD_HANDLERS = {
    # disables the s3 handler
    's3': None,
}

# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "firmware.pipelines.FirmwarePipeline" : 1,
}

# https://docs.scrapy.org/en/latest/topics/request-response.html#request-fingerprinter-implementation
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

FILES_STORE = "./output/"

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0
AUTOTHROTTLE_MAX_DELAY = 500
CONCURRENT_REQUESTS = 8

DOWNLOAD_TIMEOUT = 1200
DOWNLOAD_MAXSIZE = 0
DOWNLOAD_WARNSIZE = 0

ROBOTSTXT_OBEY = False
USER_AGENT = "FirmwareBot/1.0 (+https://github.com/firmadyne/scraper)"

#SQL_SERVER = "127.0.0.1"
