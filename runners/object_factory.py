import logging
import os

from sources.source_disabled import DisabledSource
from sources.source_json_other_1 import OneOtherJsonSource
from sources.source_json_other_2 import TwoOtherJsonSource
from sources.source_json_other_2_prepare import PrepareTwoOtherJsonSource
from sources.source_rss import RssSource
from sources.source_rss_artstation import ArtstationRssSource
from sources.source_rss_deviantart import DeviantartRssSource
from sources.source_rss_other_3 import ThreeOtherRssSource
from sources.source_rss_proxigram import ProxigramRssSource
from sources.source_rss_tiktok import TiktokRssSource
from sources.source_rss_youtube import YoutubeRssSource


logger = logging.getLogger(__name__)


class ObjectFactory:
    @staticmethod
    def create_object(href: str):
        """Create an object based on the href."""
        if not href:
            raise ValueError(f"Provided {href=} is invalid")
        elif "https://twitter.com/" in href:
            return DisabledSource(href=href)
        elif ProxigramRssSource.match(href):
            return DisabledSource(href=href)
            return ProxigramRssSource(href=href)
        elif TiktokRssSource.match(href):
            return TiktokRssSource(href=href)
        elif YoutubeRssSource.match(href):
            return YoutubeRssSource(href=href)
        elif ArtstationRssSource.match(href):
            return DisabledSource(href=href)
            return ArtstationRssSource(href=href)
        elif DeviantartRssSource.match(href):
            return DeviantartRssSource(href=href)
        elif os.environ.get("SOURCE_1_FROM") in href:
            # custom source_1 import
            return OneOtherJsonSource(href=href)
        elif os.environ.get("SOURCE_2_FROM") in href:
            # custom source_2 import
            return TwoOtherJsonSource(href=href)
        elif TwoOtherJsonSource.match(href):
            # custom source_2 import
            return TwoOtherJsonSource(href=href)
        elif PrepareTwoOtherJsonSource.match(href):
            # custom source_2 import
            return PrepareTwoOtherJsonSource(href=href)
        elif ThreeOtherRssSource.match(href):
            # custom source_3 import
            return ThreeOtherRssSource(href=href)
        else:
            # default import used for RSS
            # warning: weird stuff can be sent there
            return RssSource(href=href)
