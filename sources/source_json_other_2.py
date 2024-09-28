import json
import logging
import os

import aiohttp

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

    @classmethod
    async def __explain_from_creator_list(cls, username: str, service: str = "patreon") -> ExplainedFeed:
        href = json.loads(os.environ.get("SOURCE_2"))["creators"]
        response_str = cls.__request_via_random_proxy(href)

        if not response_str:
            # logger.warning(">>>> >>>> EMPTY RESPONSE STR")
            return
        # else:
        #     logger.warning(f">>>> >>>> {response_str=}")

        response_str = response_str.decode("utf-8")
        response_str = response_str.lstrip("[{")
        response_str = response_str.rstrip("}]")

        lst = response_str.split("},{")
        response_creators = [
            json.loads("{" + x + "}") for x in lst
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
