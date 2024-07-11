import logging

from sources.source_rss import RssSource


logger = logging.getLogger(__name__)


class ArtstationRssSource(RssSource):
    @staticmethod
    def match(href: str):
        if "artstation.com" in href:
            return True

        return False
