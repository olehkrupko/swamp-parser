import logging
from os import getenv

import random
from sentry_sdk import capture_message

from schemas.feed_explained import ExplainedFeed
from schemas.update import Update
from services.cache import Cache
from sources.source_rss import RssSource


logger = logging.getLogger(__name__)


class TiktokRssSource(RssSource):
    datetime_format = "NOW"

    @staticmethod
    def match(href: str):
        if "https://www.tiktok.com/@" in href:
            return True

        return False

    def __init__(self, href: str):
        RSS_BRIDGE_ARGS = "&".join(
            (
                "action=display",
                "bridge=TikTokBridge",
                "context=By+user",
                "format=Atom",
            )
        )

        href = href.split("?")[0]
        href = href.rstrip("/")

        timeout = random.randrange(7, 32) * 24 * 60 * 60  # 7-31 days
        username = href.split("/")[-1]

        self.href = "{0}/?{1}&username={2}&_cache_timeout={3}".format(
            getenv("RSS_BRIDGE_URL"),
            RSS_BRIDGE_ARGS,
            username,
            timeout,
        )
        self.href_original = href

    async def parse(self, response_str: str) -> list[Update]:
        parse_blocked = await Cache.get(
            type="ProxigramRssSource",
            href="parse_blocked",
        )
        if parse_blocked:
            logger.info("Skipping parse as it was called less than an hour ago.")
            return []

        # Update the cache with the current timestamp
        await Cache.set(
            type="ProxigramRssSource",
            href="parse_blocked",
            timeout={"hours": 1},
            value=True,
        )

        results = await super().parse(response_str=response_str)

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

        return results

    async def explain(self) -> ExplainedFeed:
        href = self.href_original.split("?")[0]
        username = href.split("@")[-1]

        return {
            "title": username + " - TikTok",
            "href": href,
            "href_user": "",
            "private": True,
            "frequency": "months",
            "notes": "",
            "json": {},
        }
