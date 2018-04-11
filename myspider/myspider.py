from json import dump, load

import requests
from bs4 import BeautifulSoup

from myspider.exceptions import SpiderError, LoadCookiesError, SaveCookiesError
from myspider.utils import FetchType


class MySpider:
    def __init__(self,
                 start_urls,
                 allow_domains=None,
                 headers=None,
                 cookies=None,
                 proxy=None):
        self.__session = requests.session()
        if not start_urls:
            raise SpiderError('MySpider don\'t have start urls.')
        self.setStartUrl(start_urls)
        if allow_domains:
            self.setAllowDomain(allow_domains)
        if headers:
            self.setHeader(headers)
        if cookies:
            self.setCookies(cookies)
        if proxy:
            self.setProxy(proxy)

    def setHeader(self, headers):
        """set headers of session

        Args:
            headers: A dict contain headers.

        Raises:
            ValueError: An error occurred when headers not a dict.
        """
        if not isinstance(headers, dict):
            raise ValueError('headers must be a dict')
        self.__headers = headers

    def getHeader(self):
        """get headers of session
        
        Returns:
            A dict contain session's headers.
        """
        return self.__headers

    def setCookies(self, cookies):
        """set cookies of session.

        Args:
            cookies: A dict contain cookies.

        Raises:
            ValueError: An error occurred when cookies not a dict.
        """
        if not isinstance(cookies, dict):
            raise ValueError('cookies must be a dict')
        self.__session.cookies = requests.utils.cookiejar_from_dict(cookies)

    def getCookies(self):
        """get cookies of session.

        Returns:
            A dict contain session's cookies.
        """
        return self.__session.cookies

    def saveCookies(self, filepath):
        """save session's cookie to file

        Args:
            filepath: The filepath of cookie saved.

        Raises:
            SaveCookiesError: An error occurred when any exception has been except.
        """
        cookies_dict = requests.utils.dict_from_cookiejar(
            self.__session.cookies)
        try:
            with open(filepath, 'wb') as cookies_file:
                dump(cookies_dict, cookies_file)
        except Exception as e:
            raise SaveCookiesError(e)

    def loadCookiesFromFile(self, filepath):
        """load cookie to session from file
        
        Args:
            filepath: The file path to load the cookie.

        Raises:
            LoadCookiesError: An error occurred when any exception has been except.
        """
        try:
            with open(filepath, 'rb') as cookies_file:
                cookies_dict = load(cookies_file)
                self.__session.cookies = requests.utils.cookiejar_from_dict(
                    cookies_dict)
        except Exception as e:
            raise LoadCookiesError(e)

    def setProxy(self, proxy):
        """set proxy for session.

        Args:
            proxy: A dict, like {"http": "http://10.10.1.10:3128"}.
        
        Raises:
            ValueError: An error occurred when proxy not a dict.
        """
        if not isinstance(proxy, dict):
            raise ValueError('proxy must be a dict')
        self.__proxy = proxy

    def setStartUrl(self, urls):
        """set initial urls of the spider.

        Args:
            urls: A list of urls.

        Raises:
            ValueError: An error occurred when urls not a list.
        """
        if not isinstance(urls, list):
            raise ValueError('start_urls must be a dict')
        self.__start_urls = urls

    def setAllowDomain(self, domain_list):
        """set allow domains for the spider.

        Args:
            domain_list: A list of allow domians.

        Raises:
            ValueError: An error occurred when domain_list not a list.
        """
        if not isinstance(domain_list, list):
            raise ValueError('domain_list must be a dict')
        self.__allow_domain = domain_list

    def getAllowDomain(self):
        """get allow domains of the spider.

        Returns:
            A list of spider's allow domians.
        """
        return self.__allow_domain

    def fetch(self):
        """MySpider subclasses customize crawl content by overriding this method.
        """
        pass

    def fetchImage(self,
                   parent_element_id=None,
                   parrent_element_class=None,
                   next_page_element_id=None,
                   next_page_element_class=None):
        """MySpider automatically grabs images.

        MySpider automatically grabs the img element in the parent element of
        the parent_element_id and parent_element_class lists

        Args:
            parent_element_id: The id of the image tag to grab.
            parrent_element_class: The class name of the image tag to grab.
            next_page_element_id: The id of the next page link.
            next_page_element_class: The class of the next page link.
        """

    def start(self):
        """start spider.
        """

    def __request_get(self, url, data=None):
        try:
            response = self.__session.get(
                url, data=data, headers=self.__headers, proxies=self.__proxy)
            response.raise_for_status()
        except (requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError) as e:
            print(e)
        except Exception as e:
            print(e)
        else:
            return response
