import asyncio
import os
import random
import string
from datetime import datetime
from dateutil import parser, tz  # adding custom timezones

import aiohttp
import feedparser
from sentry_sdk import capture_exception, capture_message

# import json
# import os
# import ssl
# import requests
# import urllib
# from bs4 import BeautifulSoup, SoupStrainer


async def parse_href(href: str, **kwargs: dict):
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

    #########################
    # STARTING DATA INGESTION
    #########################

    # using it as first if for now
    if False:
        return "NOPE"

    # rss-bridge instagram import converter
    elif "instagram.com" in href and not kwargs.get("processed"):
        RSS_BRIDGE_ARGS = (
            "action=display&bridge=InstagramBridge&context=Username&media_type=all"
        )

        timeout = 31 * 24 * 60 * 60  # 31 days
        username = href[26:-1]

        href = "{0}/?{1}&u={2}&_cache_timeout={3}&format=Atom".format(
            os.environ.get("RSS_BRIDGE_URL"),
            RSS_BRIDGE_ARGS,
            username,
            timeout,
        )

        results = await parse_href(
            href=href,
            processed=True,
        )
        # safeguard against failed attempts
        if len(results) == 1 and "Bridge returned error" in results[0]["name"]:
            # capture_message(f"{ href } - { results[0]['name'] }")
            return []

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
        RSS_BRIDGE_ARGS = (
            "action=display&bridge=TikTokBridge&context=By+user"
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

    # custom RSS readmanga converter
    elif "http://readmanga.live/" in href and href.find("/rss/") == -1:
        # 22 = len('http://readmanga.live/')
        name = href[22:]
        href = "https://readmanga.live/rss/manga?name=" + name

        results = await parse_href(
            href=href,
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

        results = await parse_href(
            href=href,
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

        results = await parse_href(
            href=href,
            processed=True,
        )

    # custom onlyfans import
    elif "onlyfans.com" in href:
        # TODO
        return []

    # custom patreon import
    elif "patreon.com" in href:
        # TODO
        return []

    # # custom lightnovelpub import
    # elif 'https://www.lightnovelpub.com/' in href:
    #     request = requests.get(href, headers=headers)
    #     request = BeautifulSoup(request.text, "html.parser")

    #     data = request.find('ul', attrs={'class': 'chapter-list'})
    #     if data is None:
    #         return []

    #     for each in data.find_all('li'):
    #         results.append({
    #             'name':     each.find('a')['title'],
    #             'href':     'https://www.lightnovelpub.com' \
    #                   + each.find('a')['href'],
    #             'datetime': datetime.strptime(
    #    each.find('time')['datetime'], '%Y-%m-%d %H:%M'),
    #             'feed_id':  self.id,
    #         })

    # default RSS import
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                href,
                headers=headers,
                verify_ssl=False,
            ) as response:
                # ssl._create_default_https_context = getattr(
                #     ssl, "_create_unverified_context"
                # )
                rss_str = await response.read()

        request = feedparser.parse(rss_str)

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
