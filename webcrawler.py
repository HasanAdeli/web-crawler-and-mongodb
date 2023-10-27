import requests
from time import sleep
from urllib.parse import urlparse
from extractor import url_extractor
from validator import get_valid_urls
from separator import url_separator
from database import Database


class WebCrawler:
    def __init__(self, url: str, interval: int = 0):
        self.base_url: str = url
        self.interval: int = interval
        self.project_id: str = ''
        self.db = Database()
        self.session = None
        self.set_session()

    def set_session(self):
        self.session = requests.Session()
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0'}
        )

    def send_request(self, url: str):
        print(f'A request was sent to the: {url[:50]}')
        response = self.session.get(url)
        print(f'Response status code: {response.status_code}')
        return response

    def create_new_project(self, url: str) -> None:
        project_id = self.db.add_new_project(url)
        self.db.add_url({'url': self.base_url, 'project_id': project_id, 'crawled': False, 'type': 'url'})
        self.project_id = project_id

    @staticmethod
    def extract_all_urls(base_url: str, response: requests) -> list:
        return url_extractor(base_url, response)

    @staticmethod
    def get_valid_urls(base_url: str, urls: list) -> list:
        return get_valid_urls(base_url, urls)

    @staticmethod
    def separate_urls(urls: list) -> list:
        return url_separator(urls)

    def save_all_urls(self, urls: list) -> None:
        old_urls = self.db.get_urls(self.project_id)
        new_urls = []
        for url in urls:
            if url['url'] not in old_urls:
                print(f'A new {url.get("type")} url added. [{url.get("url")}]')
                old_urls.append(url['url'])
                url['project_id'] = self.project_id
                new_urls.append(url)

        self.db.add_urls(new_urls)

    def start(self):
        print(f'crawling for "{urlparse(self.base_url).netloc}" started ...')
        self.create_new_project(self.base_url)
        while True:

            url = self.db.get_url(self.project_id)
            if not url:
                break

            response = self.send_request(url)
            if response.status_code != 200:
                self.db.update_to_crawled(url, self.project_id)
                continue

            urls = self.extract_all_urls(self.base_url, response)
            urls = self.get_valid_urls(self.base_url, urls)
            urls = self.separate_urls(urls)
            self.save_all_urls(urls)
            self.db.update_to_crawled(url, self.project_id)
            print('-' * 200)
            sleep(self.interval)
