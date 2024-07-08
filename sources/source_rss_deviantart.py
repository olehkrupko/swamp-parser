import logging

from schemas.feed import ExplainedFeed
from sources.source_rss import RssSource


logger = logging.getLogger(__name__)


class DeviantartRssSource(RssSource):
    @staticmethod
    def match(href: str):
        if "deviantart.com" in href:
            return True

        return False

    @staticmethod
    def prepare_href(href: str) -> str:
        # 27 = len('https://www.deviantart.com/')
        # 9 = len('/gallery/')
        href = href[27:-9]
        href_base = "https://backend.deviantart.com/rss.xml?type=deviation"
        href = f"{href_base}&q=by%3A{ href }+sort%3Atime+meta%3Aall"

        return href

    async def explain(self) -> ExplainedFeed:
        feed = await super().explain()

        feed["title"] += " - DeviantArt"

        return feed
