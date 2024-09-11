from seleniumwire import webdriver

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
    #"firmware.DbPipeline.DbPipeline" : 1,
    "firmware.FactPipeline.FactPipeline": 1,
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

SQL_HOST = "127.0.0.1"
SQL_PORT = 5433
SQL_DATABASE = "thesis"
SQL_USER = "thesis"
SQL_PASSWORD = "thesis"

FACT_URL = "http://127.0.0.1:5000/rest/"

from shutil import which

SELENIUM_DRIVER_NAME = 'firefox'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('geckodriver')
SELENIUM_DRIVER_ARGUMENTS=['-headless'] 
#SELENIUM_DRIVER_ARGUMENTS=[] 

SELENIUM_DRIVER_PROFILE = webdriver.FirefoxProfile()
SELENIUM_DRIVER_PREFERENCES = {
'permissions.default.stylesheet': 2,
'permissions.default.image': 2,
'dom.ipc.plugins.enabled.libflashplayer.so': 'false',
'browser.download.folderList': 2,
'browser.download.manager.showWhenStarting': False,
'browser.download.dir': '/dev/null',
'pdfjs.disabled': True,
'plugin.scan.plid.all': False,
'app.update.auto': False,
'app.update.enabled': False,
'extensions.blocklist.enabled' : False,
'browser.search.update': False,
'extensions.update.enabled': False,
'browser.shell.checkDefaultBrowser': False,
'browser.safebrowsing.downloads.remote.enabled': False,
'messaging-system.rsexperimentloader.enabled': False,
'app.shield.optoutstudies.enabled': False,
'app.normandy.enabled': False,
'browser.search.geoip.url': '',
'browser.startup.homepage_override.mstone': 'ignore',
'extensions.getAddons.cache.enabled': False,
'media.gmp-widevinecdm.enabled': False,
'media.gmp-gmpopenh264.enabled': False,
'network.captive-portal-service.enabled': False,
'network.connectivity-service.enabled': False,
'privacy.trackingprotection.enabled': False,
'privacy.trackingprotection.socialtracking.enabled': False,
}



DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'firmware.selenium.middlewares.SeleniumMiddleware': 800
}
DOWNLOAD_DELAY = 10
CONCURRENT_REQUESTS_PER_DOMAIN = 1