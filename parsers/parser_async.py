import os

import random
from sentry_sdk import capture_message

from parsers.source_json_other import OtherJsonSource
from parsers.source_rss import RssSource
from parsers.source_rss_proxigram import ProxigramRssSource

# import json
# import os
# import ssl
# import requests
# import urllib


async def parse_href(href: str, **kwargs: dict):
    ###############################
    #  PREPARING REQUIRED VARIABLES
    ###############################
    results = []

    #########################
    # STARTING DATA INGESTION
    #########################

    # using it as first if for now
    if False:
        return "NOPE"

    elif "instagram.com" in href:
        results = await ProxigramRssSource(href=href).run()

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

    # custom tiktok import
    elif "https://www.tiktok.com/@" in href and not kwargs.get("processed"):
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

        results.reverse()
        results = await parse_href(
            href=href,
            processed=True,
        )
        # safeguard against failed attempts' error messages stored as updates
        if len(results) == 1 and "Bridge returned error" in results[0]["name"]:
            capture_message(f"{ href } - { results[0]['name'] }")
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

    # custom RSS YouTube converter
    elif "https://www.youtube.com/channel/" in href:
        # 32 = len('https://www.youtube.com/channel/')
        # 7 = len('/videos')
        href_base = "https://www.youtube.com/feeds/videos.xml"
        href = f"{href_base}?channel_id={href[32:-7]}"

        results = await parse_href(
            href=href,
        )

    # custom RSS deviantart converter
    elif "deviantart.com" in href and not kwargs.get("processed"):
        # 27 = len('https://www.deviantart.com/')
        # 9 = len('/gallery/')
        href = href[27:-9]
        href_base = "https://backend.deviantart.com/rss.xml?type=deviation"
        href = f"{href_base}&q=by%3A{ href }+sort%3Atime+meta%3Aall"

        results = await parse_href(
            href=href,
            processed=True,
        )

    # custom source_1 import
    elif os.environ.get("SOURCE_1_FROM") in href:
        # prepare data
        href = href.replace(
            os.environ.get("SOURCE_1_FROM"),
            os.environ.get("SOURCE_1_TO"),
        )

        # receive data
        results = await OtherJsonSource(href=href).run()

    # custom source_2 import
    elif os.environ.get("SOURCE_2_FROM") in href:
        # prepare data
        href = href.replace(
            os.environ.get("SOURCE_2_FROM"),
            os.environ.get("SOURCE_2_TO"),
        )

        results = await OtherJsonSource(href=href).run()

    # default RSS import
    else:
        results = await RssSource(href=href).run()

    return results
