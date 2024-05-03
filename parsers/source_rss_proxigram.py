import asyncio
import os

from parsers.source_rss import RssSource

from schemas.update import Update
from services.cache import Cache


class ProxigramRssSource(RssSource):
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

    async def request(self, href: str) -> str:
        global proxigram_semaphore
        # avoiding connection overwhelming and status code 429
        proxigram_semaphore = asyncio.Semaphore(1)

        async with proxigram_semaphore:
            if os.environ["ALLOW_CACHE"] == "true":
                value = await Cache.get()
                if value is not None:
                    return value

            return await super().request(href)

    async def parse(self, response_str: str) -> list[Update]:
        results = await super().parse(response_str=response_str)

        attempt = 1
        # we constantly receive empty data
        while not results and attempt < 10:
            asyncio.sleep(3)
            print(f"ProxigramRssSource.parse() {attempt=} {results=}")

            # receive data
            response_str = await self.request(href=self.href)

            # process data
            results = await super().parse(response_str=response_str)

            attempt += 1

        if results and os.environ["ALLOW_CACHE"] == "true":
            # we are caching if data received wasn't empty
            await Cache.set(value=response_str)

        return results

    @staticmethod
    def each_name(each) -> str:
        return each["summary"]

    @staticmethod
    def parse_each(each):
        print(f">>>> { each= }")
        each["href"] = each["href"].replace(
            "http://127.0.0.1:30019",
            "https://www.instagram.com",
        )

        return each
