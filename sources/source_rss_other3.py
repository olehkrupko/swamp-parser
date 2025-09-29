import json
import logging
from os import getenv

from schemas.feed_explained import ExplainedFeed
from sources.source_rss import RssSource


logger = logging.getLogger(__name__)


class ThreeOtherRssSource(RssSource):
    environ = json.loads(getenv("SOURCE_3"))

    @classmethod
    def match(cls, href: str):
        href = href.replace("https://rt.", "https://www.")

        if cls.environ["href"]["match"] in href:
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
            self.environ["href"]["to"],
            RSS_BRIDGE_ARGS,
            type,
            username,
            3600,  # 1 hour
        )
        self.href_original = href

    async def parse(self, **kwargs) -> list:
        result = await super().parse(**kwargs)

        # ignore errors
        if len(result) == 1 and "Bridge returned error 0!" in result[0]["name"]:
            return []

        # it seems that all URLs on the page are parsed by feedparser
        # however, some of them are not valid
        result = result[:40]

        return result

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
            "json": self.environ["default"]["json"],
        }
