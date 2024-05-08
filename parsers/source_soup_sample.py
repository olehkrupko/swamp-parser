from bs4 import BeautifulSoup

from parsers.source import Source


class SampleSoupSource(Source):
    datetime_format = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def parse_each(cls, each):
        return

    @classmethod
    async def parse(cls, response_str):
        request = BeautifulSoup(response_str, "html.parser")

        data = request.find("div", attrs={"class": "card-list__items"})
        if data is None:
            return []

        return [
            {
                "name": each.find("header").text,
                "href": each.find("a")["href"],
                "datetime": cls.strptime(each.find("time")["datetime"]),
            }
            for each in data.find_all("article", attrs={"class": "post-card"})
        ]
