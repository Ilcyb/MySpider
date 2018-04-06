from json import dump, load

import requests

from myspider.exceptions import LoadCookiesError, SaveCookiesError


class MySpider:
    def __init__(self):
        self.__session = requests.session()

    def setHeader(self, headers):
        self.__headers = headers

    def getHeader(self):
        return self.__headers

    def saveCookies(self, filepath):
        """save session's cookie to file"""
        cookies_dict = requests.utils.dict_from_cookiejar(
            self.__session.cookies)
        try:
            with open(filepath, 'wb') as cookies_file:
                dump(cookies_dict, cookies_file)
        except Exception as e:
            raise SaveCookiesError(e)

    def loadCookiesFromFile(self, filepath):
        """load cookie to session from file"""
        try:
            with open(filepath, 'rb') as cookies_file:
                cookies_dict = load(cookies_file)
                self.__session.cookies = requests.utils.cookiejar_from_dict(
                    cookies_dict)
        except Exception as e:
            raise LoadCookiesError(e)
