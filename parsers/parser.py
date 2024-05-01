import feedparser
import random
import ssl
import string
import urllib
from datetime import datetime
from dateutil import parser, tz  # adding custom timezones

from sentry_sdk import capture_exception

# import os
# import json
# import requests
# from bs4 import BeautifulSoup, SoupStrainer


def parse_href(href: str, proxy: bool = True, **kwargs: dict):
    ###############################
    #  PREPARING REQUIRED VARIABLES
    ###############################

    results = []

    # avoiding blocks
    referer_domain = "".join(random.choices(string.ascii_letters, k=16))
    headers = {
        # 'user-agent': feed.UserAgent_random().strip(),
        "referer": f"https://www.{ referer_domain }.com/?q={ href }"
    }
    proxyDict = {}
    if proxy and isinstance(proxy, str):
        proxyDict["http"] = "http://" + proxy
        proxyDict["https"] = "https://" + proxy

    #########################
    # STARTING DATA INGESTION
    #########################

    # using it as first if for now
    if False:
        return "NOPE"

    # rss-bridge instagram import converter
    elif "instagram.com" in href and not kwargs.get("processed"):
        RSS_BRIDGE_URL = "http://192.168.0.155:31000"
        RSS_BRIDGE_ARGS = "&".join(
            (
                "action=display",
                "bridge=InstagramBridge",
                "context=Username",
                "media_type=all",
            )
        )

        timeout = 24 * 60 * 60  # 24 hours
        username = href[26:-1]

        href = "{0}/?{1}&u={2}&_cache_timeout={3}&format=Atom".format(
            RSS_BRIDGE_URL,
            RSS_BRIDGE_ARGS,
            username,
            timeout,
        )

        results = parse_href(
            href=href,
            proxy=proxy,
            processed=True,
        )
        # safeguard against failed attempts
        if len(results) == 1 and "Bridge returned error 401" in results[0]["name"]:
            results = []

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
    #         results = self.parse_href(proxy)
    #     except:
    #         return []

    #     base_domain = 'twitter.com'
    #     for each in results:
    #         each['href'] = each['href'].replace('#m', '')
    #         each['href'] = each['href'].replace('http://','https://')

    #         href_split = each['href'].split('/')
    #         href_split[2] = base_domain

    #         each['href'] = '/'.join(href_split)

    # custom tiktok import
    elif "https://www.tiktok.com/@" in href:
        href_base = "https://proxitok.pabloferreiro.es"
        href = f"{href_base}/@{ href.split('@')[-1] }/rss"

        results = parse_href(
            href=href,
            proxy=proxy,
        )

        results.reverse()
        for each in results:
            each["href"] = each["href"].replace(
                "proxitok.pabloferreiro.es", "tiktok.com"
            )

    # custom RSS YouTube converter
    elif "https://www.youtube.com/channel/" in href:
        # 32 = len('https://www.youtube.com/channel/')
        # 7 = len('/videos')
        href_base = "https://www.youtube.com/feeds/videos.xml"
        href = f"{href_base}?channel_id={href[32:-7]}"

        results = parse_href(
            href=href,
            proxy=proxy,
        )

    # custom RSS readmanga converter
    elif "http://readmanga.live/" in href and href.find("/rss/") == -1:
        # 22 = len('http://readmanga.live/')
        name = href[22:]
        href = "https://readmanga.live/rss/manga?name=" + name

        results = parse_href(
            href=href,
            proxy=proxy,
        )

        for each in results:
            split = each["href"].split("/")
            split[-3] = name
            each["href"] = "/".join(split)

    # custom RSS mintmanga converter
    elif (
        "mintmanga.com" in href
        and "mintmanga.com/rss/manga" not in href
        and not kwargs.get("processed")
    ):
        # 21 = len('http://mintmanga.com/')
        name = href[21:]
        href = "https://mintmanga.com/rss/manga?name=" + name

        results = parse_href(
            href=href,
            proxy=proxy,
            processed=True,
        )

        for each in results:
            split = each["href"].split("/")
            split[-3] = name
            each["href"] = "/".join(split)

    # custom RSS deviantart converter
    elif "deviantart.com" in href and not kwargs.get("processed"):
        # 27 = len('https://www.deviantart.com/')
        # 9 = len('/gallery/')
        href = href[27:-9]
        href_base = "https://backend.deviantart.com/rss.xml?type=deviation"
        href = f"{href_base}&q=by%3A{ href }+sort%3Atime+meta%3Aall"

        results = parse_href(
            href=href,
            proxy=proxy,
            processed=True,
        )

    # default RSS import
    else:
        try:
            request = feedparser.parse(href, request_headers=headers)
        except urllib.error.URLError:
            proxyDict = urllib.request.ProxyHandler(proxyDict)

            ssl._create_default_https_context = getattr(
                ssl, "_create_unverified_context"
            )
            request = feedparser.parse(
                href,
                request_headers=headers,
                handlers=[proxyDict],
            )

        for each in request["items"]:
            if not each:
                message = f"Feed {href=} is empty, skipping"
                capture_exception(message)
                continue
            try:
                result_href = each["links"][0]["href"]
            except KeyError:
                capture_exception(f"Data missing URL, skipping item {href=} {each=}")
                continue

            # DATE RESULT: parsing dates
            if "published" in each:
                result_datetime = each["published"]
            elif "delayed" in each:
                result_datetime = each["delayed"]
            elif "updated" in each:
                result_datetime = each["updated"]
            else:
                capture_exception("result_datetime broke for feed")

            tzinfos = {
                "PDT": tz.gettz("America/Los_Angeles"),
                "PST": tz.gettz("America/Juneau"),
            }
            if result_datetime.isdigit():
                result_datetime = datetime.utcfromtimestamp(int(result_datetime))
            elif not isinstance(result_datetime, datetime):
                result_datetime = parser.parse(
                    result_datetime,
                    tzinfos=tzinfos,
                )

            if each.get("title_detail"):
                result_name = each["title_detail"]["value"]
            else:
                result_name = ""

            # APPEND RESULT
            results.append(
                {
                    "name": result_name,
                    "href": result_href,
                    "datetime": result_datetime,
                }
            )

    return results
