import logging
import os

from schemas.feed_explained import ExplainedFeed
from sources.source_rss import RssSource


logger = logging.getLogger(__name__)


class ThreeOtherRssSource(RssSource):
    @staticmethod
    def match(href: str):
        href = href.replace("https://rt.", "https://www.")

        if os.environ.get("SOURCE_3")["href"]["match"] in href:
            return True

        return False

    def __init__(self, href: str):
        RSS_BRIDGE_ARGS = "&".join(
            (
                "action=display",
                "sort=%3F",
                "format=Atom",
            )
        )

        href = href.split("?")[0]
        href = href.replace("/videos", "")
        href = href.rstrip("/")
        href = href.replace("https://rt.", "https://www.")

        username = href.split("/")[-1]
        type = href.split("/")[-2]

        self.href = "{0}&{1}&type={2}&q={3}&_cache_timeout={4}".format(
            os.environ.get("SOURCE_3")["href"]["to"],
            RSS_BRIDGE_ARGS,
            type,
            username,
            3600,  # 1 hour
        )
        self.href_original = href

    async def explain(self) -> ExplainedFeed:
        result = await super().explain()

        service = result["title"].split()[0]
        title = " ".join(result["title"].split()[1:])
        title = title.split(":")[-1]
        title += f" - {service}"

        return {
            "title": title,
            "href": self.href_original,
            "href_user": "",
            "private": True,
            "frequency": "days",
            "notes": "",
            "json": os.environ.get("SOURCE_3")["default"]["json"],
        }


# ignore items with name "Bridge returned error 0! (19971)"
