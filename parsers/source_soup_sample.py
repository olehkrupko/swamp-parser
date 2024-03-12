from datetime import datetime

from bs4 import BeautifulSoup

from parsers.source import Source


class SampleSoupSource(Source):
    def _parse_each(each):
        return {
            "name": each.find('header').text,
            "href": each.find('a')['href'],
            "datetime": datetime.strptime(each.find('time')['datetime'], '%Y-%m-%d %H:%M:%S'),
        }

    @classmethod
    def parse(cls, response_str):
        results = []

        request = BeautifulSoup(response_str, "html.parser")

        data = request.find('div', attrs={'class': 'card-list__items'})
        if data is None:
            return []

        return list(map(
            lambda x: cls._parse_each(x),
            data.find_all('article', attrs={'class': 'post-card'}),
        ))
