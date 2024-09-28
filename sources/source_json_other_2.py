import aiohttp
import json
import logging
import os

from schemas.feed_explained import ExplainedFeed
from sources.source_json_other import OtherJsonSource


logger = logging.getLogger(__name__)


class TwoOtherJsonSource(OtherJsonSource):
    @staticmethod
    def match(href: str):
        if os.environ.get("SOURCE_2_FROM") in href:
            return True
        elif os.environ.get("SOURCE_2_FROM").split("/")[2] in href:
            return True

        return False

    @staticmethod
    async def __explain_from_creator_list(username: str, service: str = "patreon"):
        href = os.environ.get("SOURCE_2_TO").split("/api/v1", 1)[0]
        href += "/api/v1/creators.txt"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                href,
            ) as response:
                response_str = await response.read()
                response_str = response_str.decode("utf-8")
                response_str = response_str.lstrip("[{")
                response_str = response_str.rstrip("}]")

                response_creators = [
                    json.loads("{" + x + "}") for x in response_str.split("},{")
                ]

                for creator in response_creators:
                    if (
                        creator["service"] == service
                        and creator["name"].lower() == username.lower()
                    ):
                        return {
                            "title": username,
                            "href": os.environ.get("SOURCE_2_FROM") + creator["id"],
                            "href_user": "",
                            "private": True,
                            "frequency": "days",
                            "notes": "",
                            "json": {},
                        }

    def __init__(self, href: str):
        if os.environ.get("SOURCE_2_FROM") in href:
            self.href = href.replace(
                os.environ.get("SOURCE_2_FROM"),
                os.environ.get("SOURCE_2_TO"),
            )
        elif os.environ.get("SOURCE_2_FROM").split("/")[2] in href:
            self.href = href
        self.href_original = href

    async def explain(self) -> ExplainedFeed:
        if os.environ.get("SOURCE_2_TO") in self.href:
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
        elif os.environ.get("SOURCE_2_FROM").split("/")[2] in self.href:
            return await self.__explain_from_creator_list(
                username=self.href.split("/")[-1],
            )
