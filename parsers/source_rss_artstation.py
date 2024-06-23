import logging
import os

import feedparser
import random
from parsers.source_rss import RssSource
from sentry_sdk import capture_message

from schemas.feed import ExplainedFeed
from schemas.update import Update


logger = logging.getLogger(__name__)


class ArtstationRssSource(RssSource):
    @staticmethod
    def match(href: str):
        if "https://www.artstation.com/" in href:
            return True

        return False

    @staticmethod
    def prepare_href(href: str) -> str:
        username = href.replace("https://www.artstation.com/", "")
        username = username.strip("/")

        print(f"https://{username}.artstation.com/rss")
        return f"https://{username}.artstation.com/rss"

    async def explain(self) -> ExplainedFeed:
        channel_id = self.href.split("?channel_id=")[-1]

        feed = await super().explain()
        feed["title"] += " - YouTube"
        feed["href"] = f"https://www.youtube.com/channel/{channel_id}/videos"

        return feed
