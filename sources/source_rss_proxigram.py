import asyncio
import logging
import os
import random
from functools import reduce

from schemas.feed_explained import ExplainedFeed
from schemas.update import Update
from services.cache import Cache
from sources.source_rss import RssSource


logger = logging.getLogger(__name__)


class ProxigramRssSource(RssSource):
    @staticmethod
    def match(href: str):
        if "https://www.instagram.com/" in href:
            return True
        elif "https://instagram.com/" in href:
            return True

        return False

    def __init__(self, href: str):
        if "?" in href:
            href = href.split("?")[0]
        href = href.rstrip("/")
        href = href.replace(
            "https://instagram.com/",
            "https://www.instagram.com/",
        )
        href = href.replace("/profilecard", "")

        username = href.replace("https://www.instagram.com/", "")

        self.href = "{base}/{username}/rss".format(
            base=os.environ.get("SOURCE_PROXIGRAM_HOST"),
            username=username,
        )
        self.href_original = href

    async def request(self) -> str:
        if os.environ["ALLOW_CACHE"] is True:
            cached_value = await Cache.get(
                type="request",
                href=self.href,
            )
            if cached_value is not None:
                logger.debug(f"Successful cache retrieval for {self.href=}")
                return cached_value

        global proxigram_semaphore
        # avoiding connection overwhelming and status code 429
        proxigram_semaphore = asyncio.Semaphore(1)

        # we constantly receive empty data, so we are verifying it
        for attempt in range(1, 11):
            async with proxigram_semaphore:
                response_str = await super().request()

            results = await super().parse(
                response_str=response_str,
            )
            if results:
                logger.info(
                    f"---- ProxigramRssSource.request({self.href=}, {attempt=}) -> {len(results)=}"
                )
                if os.environ["ALLOW_CACHE"] is True:
                    await Cache.set(
                        type="request",
                        href=self.href,
                        timeout={"days": 7},
                        value=results,
                    )
                return response_str
            else:
                logger.debug(
                    f"---- ProxigramRssSource.request({self.href=}, {attempt=}) -> no results"
                )

            await asyncio.sleep(3)

        # cache failure to avoid repeats
        if os.environ["ALLOW_CACHE"] is True:
            await Cache.set(
                type="request",
                href=self.href,
                timeout={
                    "minutes": random.randint(0, 59),
                    "hours": random.randint(0, 23),
                    "days": random.randint(7, 31),
                },
                value="",
            )
        return ""

    async def parse(self, response_str: str) -> list[Update]:
        if os.environ["ALLOW_CACHE"] is True:
            parse_blocked = await Cache.get(
                type="ProxigramRssSource",
                href="parse_blocked",
            )
            if parse_blocked:
                logger.info("Skipping parse as it was called less than an hour ago.")
                return []

            # Update the cache with the current timestamp
            await Cache.set(
                type="ProxigramRssSource",
                href="parse_blocked",
                timeout={"hours": 1},
                value=True,
            )

        if response_str == "":
            return []

        results = []
        for each in await super().parse(response_str=response_str):
            each["href"] = each["href"].replace(
                "http://127.0.0.1:30019",
                "https://www.instagram.com",
            )

            if "<p>" in each["name"]:
                # logger.warning("Empty name, I guess:", each["name"], each["href"])
                each["name"] = ""
            else:
                each["name"] = each["name"].replace("&amp", "&")

            results.append(each)

        return results

    async def run(self) -> list[Update]:
        response_str = await self.request()

        # process data
        results = await super().parse(response_str=response_str)

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

    async def explain(self) -> ExplainedFeed:
        # response_str=await self.request()
        # if response_str:
        #     data = feedparser.parse(
        #         response_str=await self.request(),
        #     )

        #     return {
        #         "title": data["feed"]["title"] + " - Instagram",
        #         "href": self.href,
        #         "href_user": "",
        #         "private": True,
        #         "frequency": "days",
        #         "notes": "",
        #         "json": {},
        #     }
        # else:
        username = self.href_original.split("/")[-1]

        return {
            "title": username + " - Instagram",
            "href": self.href_original,
            "href_user": "",
            "private": True,
            "frequency": "months",
            "notes": "",
            "json": {},
        }
