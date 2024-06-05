import aiohttp
import json
import os

from parsers.source_json_other import OtherJsonSource

from schemas.feed import ExplainedFeed
from schemas.update import Update


class PrepareTwoOtherJsonSource(OtherJsonSource):
    @staticmethod
    def match(href: str):
        if os.environ.get("SOURCE_2_FROM").split("/")[2] in href:
            return True

        return False

    @staticmethod
    def prepare_href(href: str) -> str:
        return href

    async def explain(self) -> ExplainedFeed:
        href = os.environ.get("SOURCE_2_TO").split("/api/v1", 1)[0]
        href += "/api/v1/creators.txt"
        username = self.href.split("/")[-1]

        async with aiohttp.ClientSession() as session:
            async with session.get(
                href,
            ) as response:
                response_str = await response.read()

                for creator in json.loads(response_str):
                    if creator["name"] == username:
                        return {
                            "title": username,
                            "href": os.environ.get("SOURCE_2_FROM") + creator["id"],
                            "href_user": "",
                            "private": True,
                            "frequency": "days",
                            "notes": "",
                            "json": {},
                        }

        return super().explain()

    async def parse(self, response_str: str) -> list[Update]:
        return []

    async def request(self) -> str:
        return ""
