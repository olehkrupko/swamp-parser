import json
from datetime import datetime

from bs4 import BeautifulSoup

from parsers.source import Source


class OtherJsonSource(Source):
    def _parse_each(each):
        return {
            "name": each["title"],  # longer alternative: each["content"]
            "href": each["id"],
            "datetime": datetime.strptime(each["published"], '%Y-%m-%dT%H:%M:%S'),
        }

    @classmethod
    def parse(cls, response_str):
        response_data = json.loads(response_str)

        return list(map(
            lambda x: cls._parse_each(x),
            response_data,
        ))
