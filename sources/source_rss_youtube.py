import logging

import yt_dlp

from schemas.feed_explained import ExplainedFeed
from sources.source_rss import RssSource


logger = logging.getLogger(__name__)


class YoutubeRssSource(RssSource):
    @staticmethod
    def match(href: str):
        href = href.replace("https://youtube.com", "https://www.youtube.com")
        if "https://www.youtube.com/channel/" in href:
            return True
        elif "https://www.youtube.com/feeds/videos.xml?channel_id=" in href:
            return True
        elif "https://www.youtube.com" in href:
            return True

        return False

    def __init__(self, href: str):
        if "?si=" in href:
            href = href.split("?si=")[0]
        if "?sub_confirmation=" in href:
            href = href.split("?sub_confirmation=")[0]
        CHANNEL_BASE_URL = "https://www.youtube.com/feeds/videos.xml?channel_id="
        if CHANNEL_BASE_URL in href:
            channel_id = href.replace(CHANNEL_BASE_URL, "")
        elif "https://www.youtube.com/channel/" in href:
            channel_id = href.replace("https://www.youtube.com/channel/", "")
            channel_id = channel_id.replace("/videos", "")
            channel_id = channel_id.replace("?app=desktop", "")
            channel_id = channel_id.rstrip("/")
        else:
            with yt_dlp.YoutubeDL({}) as ydl:
                info = ydl.extract_info(href, process=False, download=False)
                channel_id = info["channel_id"]

        self.href = CHANNEL_BASE_URL + channel_id
        self.href_original = href

    async def parse(self, response_str: str, **kwargs) -> list:
        result = await super().parse(response_str, **kwargs)

        # Fix Shorts URLs
        for update in result:
            update.href = update.href.replace(
                "https://www.youtube.com/shorts/",
                "https://www.youtube.com/watch?v=",
            )

        return result

    async def explain(self) -> ExplainedFeed:
        channel_id = self.href.split("?channel_id=")[-1]

        feed = await super().explain()
        feed["title"] += " - YouTube"
        feed["href"] = f"https://www.youtube.com/channel/{channel_id}/videos"

        return feed
