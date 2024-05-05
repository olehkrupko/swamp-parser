import asyncio
import logging
import os

import feedparser
from parsers.source_rss import RssSource

from schemas.update import Update
from services.cache import Cache

# import html


logger = logging.getLogger(__name__)


class ProxigramRssSource(RssSource):
    @staticmethod
    def _fix_each(each: Update) -> Update:
        each["href"] = each["href"].replace(
            "http://127.0.0.1:30019",
            "https://www.instagram.com",
        )
        # lots of weird symbols, cleaning it up to proper string
        # each["name"] = (
        #     html.unescape(each["name"])
        #     # .encode("latin1")
        #     # .decode("unicode-escape")
        #     # .encode("latin1")
        #     # .decode("utf8")
        # )
        if "<p>" in each["name"]:
            logger.warning("Empty name, I guess:", each["name"], each["href"])
            each["name"] = ""

        return each

    @staticmethod
    def prepare_href(href: str) -> str:
        href = href.replace(
            "https://www.instagram.com",
            os.environ.get("SOURCE_PROXIGRAM_HOST"),
        )
        if href[-1] == "/":
            href += "rss"
        else:
            href += "/rss"

        return href

    async def request(self) -> str:
        if os.environ["ALLOW_CACHE"] == "true":
            value = await Cache.get(href=self.href)
            if value is not None:
                logger.warning(f"Successful cache retrieval for {self.href}")
                return value

        global proxigram_semaphore
        # avoiding connection overwhelming and status code 429
        proxigram_semaphore = asyncio.Semaphore(1)

        async with proxigram_semaphore:
            return await super().request()

    async def parse(self, response_str: str) -> list[Update]:
        results = await super().parse(response_str=response_str)

        attempt = 1
        # we constantly receive empty data
        while not results and attempt < 10:
            await asyncio.sleep(3)
            logger.warning(f"ProxigramRssSource.parse() {attempt=} {len(results)=}")

            # receive data
            response_str = await self.request()

            # process data
            results = await super().parse(response_str=response_str)

            attempt += 1

        if results and os.environ["ALLOW_CACHE"] == "true":
            logger.warning(f"ProxigramRssSource.parse() {attempt=} {len(results)=}")
            # we are caching if data received wasn't empty
            await Cache.set(href=self.href, value=response_str)

        if not results:
            empty = feedparser.parse(response_str)
            logger.warning(f"Still empty {empty}")
            logger.warning(f"    {empty['feed']}")
            # logger.warning(f"Still empty {response_str}")
        return [self._fix_each(x) for x in results]

    @staticmethod
    def each_name(each) -> str:
        return each["summary"]
