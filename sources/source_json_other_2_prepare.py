import aiohttp
import json
import logging
import os

from schemas.feed_explained import ExplainedFeed
from schemas.update import Update
from sources.source_json_other import OtherJsonSource


logger = logging.getLogger(__name__)


class PrepareTwoOtherJsonSource(OtherJsonSource):
    @staticmethod
    def match(href: str):
        if os.environ.get("SOURCE_2_FROM").split("/")[2] in href:
            return True

        return False

    def __init__(self, href: str):
        self.href = href
        self.href_original = href

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
