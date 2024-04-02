import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Union

import requests
from bs4 import BeautifulSoup, ResultSet

# Load logger
logger = logging.getLogger(__name__)


class Scraper(ABC):
    def __init__(self, urls: List[str]) -> None:
        self.urls = urls

    @abstractmethod
    def extract(self) -> Dict:
        raise NotImplementedError("Extract method must be implemented by subclasses")


class PromiedosScraper(Scraper):
    def __init__(self, urls) -> None:
        super().__init__(urls)
        self.scraper_content = self._get_scraper_contents(urls)

    def _get_scraper_contents(self, urls: List[str]) -> Dict[str, BeautifulSoup]:
        contents = {}
        for url in urls:
            page = requests.get(url)
            contents[url] = BeautifulSoup(page.text, 'html.parser')
        return contents

    def extract(self, entity: str = "matches", period: str = "yesterday") -> Union[ResultSet, None]:
        if entity == "matches" and period == "yesterday":
            url_yesterday_matches = "https://www.promiedos.com.ar/ayer"
            if url_yesterday_matches in self.scraper_content.keys():
                logger.debug(f'Extracting data from {url_yesterday_matches}...')
                return self.scraper_content[url_yesterday_matches].find_all(id="fixturein")
