import asyncio
import logging
import os
from functools import reduce

import feedparser
from parsers.source_rss import RssSource

from schemas.feed import ExplainedFeed
from schemas.update import Update
from services.cache import Cache


logger = logging.getLogger(__name__)


class ProxigramRssSource(RssSource):
    @staticmethod
    def _fix_each(each: Update) -> Update:
        each["href"] = each["href"].replace(
            "http://127.0.0.1:30019",
            "https://www.instagram.com",
        )

        if "<p>" in each["name"]:
            # logger.warning("Empty name, I guess:", each["name"], each["href"])
            each["name"] = ""
        else:
            each["name"] = each["name"].replace("&amp", "&")

        return each

    async def explain(self) -> ExplainedFeed:
        response_str = await self.request()
        data = feedparser.parse(response_str)

        return {
            "title": data["feed"]["title"] + " - Instagram",
            "href": self.href,
            "href_user": "",
            "private": True,
            "frequency": "days",
            "notes": "",
            "json": {},
        }

    @staticmethod
    def prepare_href(href: str) -> str:
        if "?" in href:
            href = href.split("?")[0]

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
        global proxigram_semaphore
        # avoiding connection overwhelming and status code 429
        proxigram_semaphore = asyncio.Semaphore(1)

        async with proxigram_semaphore:
            return await super().request()

    @staticmethod
    def each_name(each) -> str:
        return each["summary"]

    def cleanup(self, results: list) -> list:
        # remove duplicates
        # it seems to be caused by pinned posts
        href_dict = {}
        for each in results:
            if each["href"] not in href_dict.keys():
                href_dict[each["href"]] = [each]
            else:
                href_dict[each["href"]].append(each)
        # remove newer duplicates
        for key, value in href_dict.items():
            # we expect two posts with one href max, but reduce sounds cool
            href_dict[key] = reduce(
                lambda a, b: a if a["datetime"] < b["datetime"] else b, value
            )
        # remove duplicates from results
        results = list(filter(lambda x: (x in href_dict.values()), results))

        return [self._fix_each(x) for x in results]

    async def run(self) -> list[Update]:
        # receive data
        if os.environ["ALLOW_CACHE"] == "true":
            value = await Cache.get(href=self.href, type="processed")
            if value is not None:
                # logger.warning(f"Successful cache retrieval for {self.href}")
                return value

        response_str = await self.request()

        # process data
        results = await super().parse(response_str=response_str)

        attempt = 0
        # we constantly receive empty data
        while not results and attempt < 10:
            attempt += 1
            await asyncio.sleep(3)
            # logger.warning(
            #     f"---- ProxigramRssSource.request({self.href=}, {attempt=}) -> {len(results)=}"
            # )

            # receive data
            response_str = await self.request()

            # process data
            results = await super().parse(response_str=response_str)
            if not results:
                empty = feedparser.parse(response_str)
                if empty["feed"].get("id", None):
                    # private account or no posts
                    break

        if results and os.environ["ALLOW_CACHE"] == "true":
            # logger.warning(
            #     f"---- ProxigramRssSource.request({self.href=}, {attempt=}) -> {len(results)=}"
            # )
            # we are caching if data received wasn't empty
            await Cache.set(
                href=self.href,
                type="processed",
                timeout={"days": 7},
                value=results,
            )

        results = self.cleanup(results)
        logger.warning(
            f"---- ProxigramRssSource.request({self.href=}, {attempt=}) -> {len(results)=}"
        )
        return results
