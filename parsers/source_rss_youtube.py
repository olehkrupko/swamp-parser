import logging

from parsers.source_rss import RssSource

from schemas.feed import ExplainedFeed


logger = logging.getLogger(__name__)


class YoutubeRssSource(RssSource):
    @staticmethod
    def match(href: str):
        if "https://www.youtube.com/channel/" in href:
            return True
        elif "https://www.youtube.com/feeds/videos.xml?channel_id=" in href:
            return True

        return False

    @staticmethod
    def prepare_href(href: str) -> str:
        if "https://www.youtube.com/feeds/videos.xml?channel_id=" in href:
            return href

        HREF_BASE = "https://www.youtube.com/feeds/videos.xml"

        channel_id = href.replace("https://www.youtube.com/channel/", "")
        channel_id = channel_id.replace("/videos", "")
        channel_id = channel_id.strip("/")

        return f"{HREF_BASE}?channel_id={channel_id}"

    async def explain(self) -> ExplainedFeed:
        channel_id = self.href.split("?channel_id=")[-1]

        feed = await super().explain()
        feed["title"] += " - YouTube"
        feed["href"] = f"https://www.youtube.com/channel/{channel_id}/videos"

        return feed
