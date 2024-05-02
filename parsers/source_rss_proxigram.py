import asyncio
import os

from parsers.source_rss import RssSource


class ProxigramRssSource(RssSource):
    @staticmethod
    def prepare_href(href):
        href = href.replace(
            "https://www.instagram.com",
            os.environ.get("SOURCE_PROXIGRAM_HOST"),
        )
        if href[-1] == "/":
            href += "rss"
        else:
            href += "/rss"

        return href

    async def request(self, href):
        global proxigram_semaphore
        # avoiding connection overwhelming and status code 429
        proxigram_semaphore = asyncio.Semaphore(1)

        async with proxigram_semaphore:
            return await super().request(href)

    async def parse(self, response_str: str):
        results = await super().parse(response_str=response_str)

        attempt = 1
        while not results and attempt < 10:
            asyncio.sleep(3)
            print(f"ProxigramRssSource.parse() {attempt=} {results=}")

            # receive data
            response_str = await self.request(href=self.href)

            # process data
            results = await super().parse(response_str=response_str)

            attempt += 1

        return results

    @staticmethod
    def each_name(each):
        return each["summary"]

    @staticmethod
    def parse_each(each):
        print(f">>>> { each= }")
        each["href"] = each["href"].replace(
            "http://127.0.0.1:30019",
            "https://www.instagram.com",
        )

        return each
