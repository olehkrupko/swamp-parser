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
        # print("Parser not supported for now")
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

    # # rss-bridge instagram import converter
    # elif "instagram.com" in href and not kwargs.get("processed"):
    #     RSS_BRIDGE_ARGS = "&".join(
    #         (
    #             "action=display",
    #             # "bridge=InstagramBridge",
    #             "bridge=PicnobBridge",
    #             "context=Username",
    #             # "media_type=all",
    #         )
    #     )

    #     timeout = 31 * 24 * 60 * 60  # 31 days
    #     username = href[26:-1]

    #     href = "{0}/?{1}&u={2}&_cache_timeout={3}&format=Atom".format(
    #         os.environ.get("RSS_BRIDGE_URL"),
    #         RSS_BRIDGE_ARGS,
    #         username,
    #         timeout,
    #     )

    #     results = await parse_href(
    #         href=href,
    #         processed=True,
    #     )
    #     # safeguard against failed attempts
    #     if len(results) == 1 and "Bridge returned error" in results[0]["name"]:
    #         # capture_message(f"{ href } - { results[0]['name'] }")
    #         return []

    # # custom twitter import converter
    # elif 'https://twitter.com/' in self.href:
    #     self.href_user = self.href[:]
    #     caching_servers = (
    #         'https://nitter.net',
    #         'https://nitter.42l.fr',  # +
    #         'https://nitter.nixnet.services',  # x
    #         'https://nitter.pussthecat.org',
    #         'https://nitter.mastodont.cat',
    #         'https://nitter.tedomum.net',  # xx
    #         'https://nitter.fdn.fr',
    #         'https://nitter.1d4.us',
    #         'https://nitter.kavin.rocks',
    #         'https://tweet.lambda.dance',  # xx
    #         'https://nitter.cc',
    #         'https://nitter.weaponizedhumiliation.com',  # x
    #         'https://nitter.vxempire.xyz',
    #         'https://nitter.unixfox.eu',
    #         'https://nitter.himiko.cloud',  # x
    #         'https://nitter.eu',
    #         'https://nitter.ethibox.fr',   # x
    #         'https://nitter.namazso.eu',  # +
    #     )
    #     # 20 = len('https://twitter.com/')
    #     server = random.choice(caching_servers)
    #     self.href = f"{ server }/{ self.href[20:] }/rss"

    #     try:
    #         results = self.parse_href()
    #     except:
    #         return []

    #     base_domain = 'twitter.com'
    #     for each in results:
    #         each['href'] = each['href'].replace('#m', '')
    #         each['href'] = each['href'].replace('http://', 'https://')

    #         href_split = each['href'].split('/')
    #         href_split[2] = base_domain

    #         each['href'] = '/'.join(href_split)

    # # custom tiktok import
    # elif "https://www.tiktok.com/@" in href:
    #     href_base = "https://proxitok.pabloferreiro.es"
    #     href = f"{href_base}/@{ href.split('@')[-1] }/rss"

    #     results = await parse_href(
    #         href=href,
    #     )

    #     results.reverse()
    #     for each in results:
    #         each["href"] = each["href"].replace(
    #             "proxitok.pabloferreiro.es", "tiktok.com"
    #         )
