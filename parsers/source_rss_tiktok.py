import logging
import os

import feedparser
import random
from parsers.source_rss import RssSource
from sentry_sdk import capture_message

from schemas.feed import ExplainedFeed
from schemas.update import Update


logger = logging.getLogger(__name__)


class TiktokRssSource(RssSource):
    @staticmethod
    def prepare_href(href: str) -> str:
        RSS_BRIDGE_ARGS = "&".join(
            (
                "action=display",
                "bridge=TikTokBridge",
                "context=By+user",
            )
        )

        timeout = random.randrange(7, 32) * 24 * 60 * 60  # 7-31 days
        username = href[24:]

        href = "{0}/?{1}&username={2}&_cache_timeout={3}&format=Atom".format(
            os.environ.get("RSS_BRIDGE_URL"),
            RSS_BRIDGE_ARGS,
            username,
            timeout,
        )

        return href

    async def explain(self) -> ExplainedFeed:
        response_str = await self.request()
        data = feedparser.parse(response_str)

        return {
            "title": data["feed"]["title"],
            "href": self.href,
            "href_user": "",
            "private": True,
            "frequency": "days",
            "notes": "",
            "json": {},
        }

    async def parse(self, response_str: str) -> list[Update]:
        results = super().parse(response_str=response_str)

        # safeguard against failed attempts' error messages stored as updates
        if len(results) == 1 and "Bridge returned error" in results[0]["name"]:
            capture_message(f"{ self.href } - { results[0]['name'] }")
            results = []

        # reversing order to sort data from old to new
        results.reverse()
        for index, each in enumerate(results):
            # parser returns each["name"] == "Video" by default
            each["name"] = "" if each["name"] == "Video" else each["name"]
            # and it uses current datetime as well
            # seconds are added so we could properly order data by datetime
            each["datetime"] = each["datetime"].replace(second=index)
            # the only valid data there is a URL. But at least it works!
