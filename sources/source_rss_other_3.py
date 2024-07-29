import logging
import os

import random
from sentry_sdk import capture_message

from schemas.feed_explained import ExplainedFeed
from schemas.update import Update
from sources.source_rss import RssSource


logger = logging.getLogger(__name__)


class ThreeOtherRssSource(RssSource):
    @staticmethod
    def match(href: str):
        if os.environ.get("SOURCE_3_FROM") in href:
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
        href = href.rstrip("/")

        username = href.split("/")[-1]

        self.href = "{0}&{1}&q={2}&_cache_timeout={3}".format(
            os.environ.get("SOURCE_3_TO"),
            RSS_BRIDGE_ARGS,
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
            "json": {},
        }
