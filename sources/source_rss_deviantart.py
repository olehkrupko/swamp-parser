import logging

from schemas.feed_explained import ExplainedFeed
from sources.source_rss import RssSource


logger = logging.getLogger(__name__)


class DeviantartRssSource(RssSource):
    @staticmethod
    def match(href: str):
        if "deviantart.com" in href:
            return True

        return False

    def __init__(self, href: str):
        HREF_BASE = "https://backend.deviantart.com/rss.xml?type=deviation"

        username = href.split("deviantart.com/")[-1]
        username = username.split("/")[0]

        self.href = f"{ HREF_BASE }&q=by%3A{ username }+sort%3Atime+meta%3Aall"
        self.href_original = href

    async def explain(self) -> ExplainedFeed:
        feed = await super().explain()

        feed["title"] = feed["title"].replace("DeviantArt: ", "")
        feed["title"] += " - DeviantArt"

        feed["href"] = self.href_original
        if "/gallery" not in feed["href"]:
            feed["href"] += "/gallery"

        feed["private"] = True

        return feed
