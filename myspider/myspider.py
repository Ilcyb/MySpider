from json import dump, load
from os.path import join
import queue

import requests
from bs4 import BeautifulSoup

from myspider.exceptions import SpiderError, LoadCookiesError, SaveCookiesError
from myspider.utils import FetchType, mymd5


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
        self.__next_urls = queue.Queue()
        self.__put_start_urls_to_next()

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

    def fetchImage(
            self,
            image_save_path,
            parent_element_id=None,
            parrent_element_class=None,
            next_page_element_id=None,
            next_page_element_class=None,
    ):
        """MySpider automatically grabs images.

        MySpider automatically grabs the img element in the parent element of
        the parent_element_id and parent_element_class lists

        Args:
            image_save_path: directory path for storing pictures.
            parent_element_id: The id list of the image tag to grab.
            parrent_element_class: The class name list of the image tag to grab.
            next_page_element_id: The id list of the next page link.
            next_page_element_class: The class list of the next page link.
        """
        while True:
            url = self.__next_urls.get()
            response = self.__request_get(url)
            self.__fetchImage(
                response.text,
                r'C:\Users\hybma\Pictures\爬取图片',
                parent_element_id=parent_element_id,
                parrent_element_class=parrent_element_class,
                next_page_element_id=next_page_element_id,
                next_page_element_class=next_page_element_class)

    def __fetchImage(self,
                     page_content,
                     save_path,
                     parent_element_id=None,
                     parrent_element_class=None,
                     next_page_element_id=None,
                     next_page_element_class=None):
        page_doc = BeautifulSoup(page_content, "html.parser")

        parent_elements = page_doc.find_all(attrs={
            "class": parrent_element_class
        }) if parrent_element_class != None else []
        parent_elements += page_doc.find_all(attrs={
            "id": parent_element_id
        }) if parent_element_id != None else []

        next_elements = page_doc.find_all(attrs={
            "class": next_page_element_class
        }) if next_page_element_class != None else []
        next_elements += page_doc.find_all(attrs={
            "id": next_page_element_id
        }) if next_page_element_id != None else []

        img_urls = list()
        for element in parent_elements:
            img_elements = element.find_all('img')
            for img_element in img_elements:
                img_urls.append(img_element['src'])

        next_urls = list()
        for element in next_elements:
            url_elements = element.find_all('a')
            for url_element in url_elements:
                next_urls.append(url_element['href'])

        self.__add_url_to_next(next_urls)
        self.__save_imgs_to_local(save_path, img_urls)

    def __save_imgs_to_local(self, save_path, url_list):
        for url in url_list:
            self.__save_img_to_local(save_path, url)

    def __save_img_to_local(self, save_path, url):
        img_response = self.__request_get(url)
        complete_path = join(save_path, mymd5(url)) + '.jpg'
        with open(complete_path, 'wb') as img_f:
            img_f.write(img_response.content)

    def __add_url_to_next(self, url_list):
        for url in url_list:
            self.__next_urls.put(url)

    def start(self):
        """start spider.
        """

    def __request_get(self, url, data=None):
        try:
            response = self.__session.get(
                url, data=data,
                headers=self.__headers if hasattr(self, '__headers') else None,
                proxies=self.__proxy if hasattr(self, '__proxy') else None)
            response.raise_for_status()
        except (requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError) as e:
            print(e)
        except Exception as e:
            print(e)
        else:
            return response

    def __put_start_urls_to_next(self):
        for url in self.__start_urls:
            self.__next_urls.put(url)
