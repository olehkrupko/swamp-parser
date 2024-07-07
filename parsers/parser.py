import os

from parsers.source_disabled import DisabledSource
from parsers.source_json_other_1 import OneOtherJsonSource
from parsers.source_json_other_2 import TwoOtherJsonSource
from parsers.source_json_other_2_prepare import PrepareTwoOtherJsonSource
from parsers.source_rss import RssSource
from parsers.source_rss_artstation import ArtstationRssSource
from parsers.source_rss_deviantart import DeviantartRssSource
from parsers.source_rss_proxigram import ProxigramRssSource
from parsers.source_rss_tiktok import TiktokRssSource
from parsers.source_rss_youtube import YoutubeRssSource

# import json
# import os
# import ssl
# import requests
# import urllib


def object_factory(href):
    if not href:
        raise ValueError(f"Provided {href=} is invalid")
    elif "https://twitter.com/" in href:
        # print("TODO: Parser not supported for now")
        return DisabledSource(href=href)
    elif "instagram.com" in href:
        return ProxigramRssSource(href=href)
    elif "https://www.tiktok.com/@" in href:
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
    else:
        # default import used for RSS
        # warning: weird stuff can be sent there
        return RssSource(href=href)


async def explain_feed(href: str):
    return await object_factory(href=href).explain()


async def parse_href(href: str, **kwargs: dict):
    return await object_factory(href=href).run()
