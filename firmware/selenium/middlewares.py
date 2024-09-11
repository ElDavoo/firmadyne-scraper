"""This module contains the ``SeleniumMiddleware`` scrapy middleware"""

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse
from seleniumwire import webdriver
import socket

from selenium.webdriver.remote.command import Command
from selenium.webdriver.support.ui import WebDriverWait

from .http import SeleniumRequest


class SeleniumMiddleware:
    """Scrapy middleware handling the requests using selenium"""

    @staticmethod
    def is_alive(driver):
        try:
            driver.execute(Command.GET_TITLE)
            return True
        except Exception as e :
            return False
        return False


    def __init__(self, driver_name, command_executor, driver_arguments, driver_profile = None, driver_preferences = None):
    # def __init__(self, driver_name, driver_executable_path,
    #     browser_executable_path, command_executor, driver_arguments):
        """Initialize the selenium webdriver

        Parameters
        ----------
        driver_name: str
            The selenium ``WebDriver`` to use
        driver_executable_path: str
            The path of the executable binary of the driver
        driver_arguments: list
            A list of arguments to initialize the driver
        browser_executable_path: str
            The path of the executable binary of the browser
        command_executor: str
            Selenium remote server endpoint
        """

        self.driver_name = driver_name.lower().capitalize()

        self.driver_options = getattr(webdriver, f"{self.driver_name}Options")()
        if driver_preferences is not None:
            for argument in driver_arguments:
                self.driver_options.add_argument(argument)
        
        #Tested only with Firefox
        if driver_profile:
            for key, value in driver_preferences.items():
                driver_profile.set_preference(key, value)
            self.driver_options.profile = driver_profile

        self.command_executor = command_executor
        self.drivers = {}

    def new_driver(self):
        if self.command_executor:
            return webdriver.Remote(command_executor=self.command_executor,
                                           options=self.driver_options)
        driver_class = getattr(webdriver, self.driver_name)
        return driver_class(options=self.driver_options)

    @classmethod
    def from_crawler(cls, crawler):
        """Initialize the middleware with the crawler settings"""

        driver_name = crawler.settings.get('SELENIUM_DRIVER_NAME')
        command_executor = crawler.settings.get('SELENIUM_COMMAND_EXECUTOR')
        driver_arguments = crawler.settings.get('SELENIUM_DRIVER_ARGUMENTS')
        driver_profile = crawler.settings.get('SELENIUM_DRIVER_PROFILE')
        driver_preferences = crawler.settings.get('SELENIUM_DRIVER_PREFERENCES')

        if driver_name is None:
            raise NotConfigured('SELENIUM_DRIVER_NAME must be set')

        middleware = cls(
            driver_name=driver_name,
            command_executor=command_executor,
            driver_arguments=driver_arguments,
            driver_profile=driver_profile,
            driver_preferences=driver_preferences
        )

        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

        return middleware

    def process_request(self, request, spider):
        """Process a request using the selenium driver if applicable"""

        if not isinstance(request, SeleniumRequest):
            return None
        
        url = request.url

        # Find a driver from the request url in the dictionary, if not, create it
        if url not in self.drivers:
            self.drivers[url] = self.new_driver()
        
        if not SeleniumMiddleware.is_alive(self.drivers[url]):
            self.drivers[url] = self.new_driver()
        

        if request.scopes:
            self.drivers[url].scopes = request.scopes

        self.drivers[url].get(request.url)

        for cookie_name, cookie_value in request.cookies.items():
            self.drivers[url].add_cookie(
                {
                    'name': cookie_name,
                    'value': cookie_value
                }
            )

        if request.wait_until:
            WebDriverWait(self.drivers[url], request.wait_time).until(
                request.wait_until
            )

        if request.screenshot:
            request.meta['screenshot'] = self.drivers[url].get_screenshot_as_png()

        if request.script:
            self.drivers[url].execute_script(request.script)

        body = str.encode(self.drivers[url].page_source)

        # Expose the driver via the "meta" attribute
        request.meta.update({'driver': self.drivers[url]})

        return HtmlResponse(
            self.drivers[url].current_url,
            body=body,
            encoding='utf-8',
            request=request
        )

    def spider_closed(self):
        """Shutdown the driver when spider is closed"""

        for driver in self.drivers.values():
            driver.quit()
        self.drivers = {}
