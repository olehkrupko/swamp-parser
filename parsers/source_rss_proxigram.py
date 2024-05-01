import os

from parsers.source_rss import RssSource


class ProxigramRssSource(RssSource):
    @staticmethod
    def prepare_href(href):
        href = href.replace(
            "https://www.instagram.com",
            os.environ.get("SOURCE_PROXIGRAM_HOST"),
        )
        if href[-1] == "/":
            href += "rss"
        else:
            href += "/rss"

        return href

    @staticmethod
    def each_name(each):
        return each["summary"]

    @staticmethod
    def parse_each(each):
        each["href"] = each["href"].replace(
            "http://127.0.0.1:30020",
            "https://www.instagram.com",
        )

        return each
