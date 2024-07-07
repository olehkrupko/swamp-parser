import logging

from parsers.source_rss import RssSource


logger = logging.getLogger(__name__)


class ArtstationRssSource(RssSource):
    @staticmethod
    def match(href: str):
        if "https://www.artstation.com/" in href:
            return True

        # TODO: remove later
        # it's left there to stop DDOSing unresponsive RSS
        if "artstation.com/" in href:
            return True

        return False
