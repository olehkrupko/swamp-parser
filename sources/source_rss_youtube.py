import logging

from schemas.feed_explained import ExplainedFeed
from sources.source_rss import RssSource


logger = logging.getLogger(__name__)


class YoutubeRssSource(RssSource):
    @staticmethod
    def match(href: str):
        if "https://www.youtube.com" in href and "@" in href:
            raise ValueError("@ channel username not supported")
        elif "https://www.youtube.com/channel/" in href:
            return True
        elif "https://www.youtube.com/feeds/videos.xml?channel_id=" in href:
            return True

        return False

    def __init__(self, href: str):
        CHANNEL_BASE_URL = "https://www.youtube.com/feeds/videos.xml?channel_id="
        if CHANNEL_BASE_URL in href:
            channel_id = href.replace(CHANNEL_BASE_URL, "")
        else:
            channel_id = href.replace("https://www.youtube.com/channel/", "")
            channel_id = channel_id.replace("/videos", "")
            channel_id = channel_id.replace("?app=desktop", "")
            channel_id = channel_id.rstrip("/")

        self.href = CHANNEL_BASE_URL + channel_id
        self.href_original = href

    async def explain(self) -> ExplainedFeed:
        channel_id = self.href.split("?channel_id=")[-1]

        feed = await super().explain()
        feed["title"] += " - YouTube"
        feed["href"] = f"https://www.youtube.com/channel/{channel_id}/videos"

        return feed
