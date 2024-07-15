import aiohttp
import json
import os

from schemas.feed_explained import ExplainedFeed
from sources.source_json_other import OtherJsonSource


class OneOtherJsonSource(OtherJsonSource):
    def __init__(self, href: str):
        self.href = href.replace(
            os.environ.get("SOURCE_1_FROM"),
            os.environ.get("SOURCE_1_TO"),
        )
        self.href_original = href

    async def explain(self) -> ExplainedFeed:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.href + "/profile",
            ) as response:
                response_str = await response.read()
                data = json.loads(response_str)

                return {
                    "title": data["name"],
                    "href": self.href_original,
                    "href_user": "",
                    "private": True,
                    "frequency": "days",
                    "notes": "",
                    "json": {},
                }
