import aiohttp
import json
import logging
from os import getenv

from schemas.feed_explained import ExplainedFeed
from sources.source_json_other import OtherJsonSource


logger = logging.getLogger(__name__)


class OneOtherJsonSource(OtherJsonSource):
    def __init__(self, href: str):
        self.href = href.replace(
            getenv("SOURCE_1_FROM"),
            getenv("SOURCE_1_TO"),
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
