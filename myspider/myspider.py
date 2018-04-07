from json import dump, load

import requests

from myspider.exceptions import LoadCookiesError, SaveCookiesError


class MySpider:
    def __init__(self):
        self.__session = requests.session()

    def setHeader(self, headers):
        """set headers of session

        Args:
            headers: A dict contain headers.
        """
        self.__headers = headers

    def getHeader(self):
        """get headers of session
        
        Returns:
            A dict contain session's headers.
        """
        return self.__headers

    def saveCookies(self, filepath):
        """save session's cookie to file

        Args:
            filepath: The filepath of cookie saved.
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
        """
        self.__proxy = proxy

    def setStartUrl(self, urls):
        """set initial urls of the spider.

        Args:
            urls: A list of urls.
        """
        self.__start_urls = urls

    def setAllowDomain(self, domain_list):
        """set allow domains for the spider.

        Args:
            domain_list: A list of allow domians.
        """
        self.__allow_domain = domain_list

    def getAllowDomain(self):
        """get allow domains of the spider.

        Returns:
            A list of spider's allow domians.
        """
        return self.__allow_domain
