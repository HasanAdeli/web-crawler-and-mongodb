from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class AbstractExtractor(ABC):
    def __init__(self, base_url):
        self.base_url = base_url

    @abstractmethod
    def extract(self, source_code):
        pass


class UrlsExtractor(AbstractExtractor):
    def __init__(self, base_url):
        super().__init__(base_url)

    def extract(self, source_code):
        return [
            {'url': urljoin(self.base_url, tag.get('href')), 'crawled': False, 'type': 'url'}
            for tag in source_code.find_all('a') if tag.get('href')
        ]


class CssUrlsExtractor(AbstractExtractor):
    def __init__(self, base_url):
        super().__init__(base_url)

    def extract(self, source_code):
        return [
            {'url': urljoin(self.base_url, tag.get('href')), 'crawled': False, 'type': 'css_url'}
            for tag in source_code.find_all('link') if tag.get('href') and tag.get('rel')[0] == 'stylesheet'
        ]


class JsUrlsExtractor(AbstractExtractor):
    def __init__(self, base_url):
        super().__init__(base_url)

    def extract(self, source_code):
        return [
            {'url': urljoin(self.base_url, tag.get('src')), 'crawled': False, 'type': 'js_url'}
            for tag in source_code.find_all('script') if tag.get('src')
        ]


class ImgUrlsExtractor(AbstractExtractor):
    def __init__(self, base_url):
        super().__init__(base_url)

    def extract(self, source_code):
        return (
                [
                    {'url': urljoin(self.base_url, tag.get('src')), 'crawled': False, 'type': 'img_url'}
                    for tag in source_code.find_all('img') if tag.get('src')
                ]
                +
                [
                    {'url': urljoin(self.base_url, tag.get('data-src')), 'crawled': False, 'type': 'img_url'}
                    for tag in source_code.find_all('img') if tag.get('data-src')
                ]
        )


class VideoUrlsExtractor(AbstractExtractor):
    def __init__(self, base_url):
        super().__init__(base_url)

    def extract(self, source_code):
        return [
            {'url': urljoin(self.base_url, tag.get('src')), 'crawled': False, 'type': 'video_url'}
            for tag in source_code.find_all('video') if tag.get('src')
        ]


class AudioUrlsExtractor(AbstractExtractor):
    def __init__(self, base_url):
        super().__init__(base_url)

    def extract(self, source_code):
        return [
            {'url': urljoin(self.base_url, tag.get('src')), 'crawled': False, 'type': 'audio_url'}
            for tag in source_code.find_all('audio') if tag.get('src')
        ]


def url_extractor(base_url: str, response) -> list:
    all_urls = []
    source_code = BeautifulSoup(response.text, 'html.parser')
    for sub_class in AbstractExtractor.__subclasses__():
        extractor = sub_class(base_url)
        new_urls = extractor.extract(source_code)
        all_urls.extend(new_urls)
    return all_urls
