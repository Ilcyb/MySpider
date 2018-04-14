from json import dump, load
from os.path import join, exists, isdir
from os import makedirs
from logging import DEBUG, INFO, WARN, ERROR, CRITICAL
import queue

import requests
from bs4 import BeautifulSoup

from myspider.exceptions import SpiderError, LoadCookiesError, SaveCookiesError, DirectoryNotExistsError, \
    NotDirectoryError
from myspider.utils import FetchType, mymd5
from myspider.logger import log


class MySpider:
    def __init__(self,
                 start_urls,
                 allow_domains=None,
                 headers=None,
                 cookies=None,
                 proxy=None):
        try:
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
        except (ValueError, SpiderError) as e:
            log(e, ERROR)
            exit()
        except Exception as e:
            from traceback import print_exc
            print_exc()

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
            ValueError: An error occurred when urls not a list or a string that can be converted to a list.
        """
        urls = self.__check_is_list_or_can_convert2list(urls, 'urls')
        self.__start_urls = urls

    def setAllowDomain(self, domain_list):
        """set allow domains for the spider.

        Args:
            domain_list: A list of allow domians.

        Raises:
            ValueError: An error occurred when domain_list not a list.
        """
        domain_list = self.__check_is_list_or_can_convert2list(
            domain_list, 'domain_list')
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

        if not exists(image_save_path):
            makedirs(image_save_path)
            log('The directory pointed to by img_save_path does not exist. \
            The directory has been automatically created.')

        if not isdir(image_save_path):
            raise NotDirectoryError(
                'The path pointed to by img_save_path not a directory')

        all_none_flag = True
        for name, param in {
            'parent_element_id': parent_element_id, 
            'parrent_element_class': parrent_element_class, 
            'next_page_element_id': next_page_element_id,
            'next_page_element_class': next_page_element_class
        }.items():
            if param is not None:
                param = self.__check_is_list_or_can_convert2list(param, name)
                all_none_flag = False

        if all_none_flag:
            raise SpiderError('missing enough parameters to fetch image')

        self.__take_out_url_and_get_response_and_execute_function(
            self.__fetchImage,
            image_save_path,
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

        parent_elements = page_doc.find_all(
            attrs={"class": parrent_element_class
                   }) if parrent_element_class != None else []
        parent_elements += page_doc.find_all(
            attrs={"id": parent_element_id
                   }) if parent_element_id != None else []

        next_elements = page_doc.find_all(
            attrs={"class": next_page_element_class
                   }) if next_page_element_class != None else []
        next_elements += page_doc.find_all(
            attrs={"id": next_page_element_id
                   }) if next_page_element_id != None else []

        img_urls = list()
        for element in parent_elements:
            img_elements = element.find_all('img')
            for img_element in img_elements:
                src = img_element.get('src')
                if src is not None:
                    img_urls.append(src)

        next_urls = list()
        for element in next_elements:
            url_elements = element.find_all('a')
            for url_element in url_elements:
                href = url_element.get('href')
                if href is not None:
                    next_urls.append(href)

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
                url,
                data=data,
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

    def __check_is_list_or_can_convert2list(self, target, name):
        if not isinstance(target, list):
            if not isinstance(target, str):
                raise ValueError(
                    '{} must be a list or a string that can be converted to a list'.
                    format(name))
            target = list(target)
        return target

    def __take_out_url_and_get_response_and_execute_function(
            self, func, *args, **kwargs):
        while True:
            url = self.__next_urls.get()
            response = self.__request_get(url)
            args = list(args)
            args.insert(0, response.text)
            func(*args, **kwargs)
