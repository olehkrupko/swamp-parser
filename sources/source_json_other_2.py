import json
import logging
import os

import aiohttp

from schemas.feed_explained import ExplainedFeed
from sources.source_json_other import OtherJsonSource


logger = logging.getLogger(__name__)


class TwoOtherJsonSource(OtherJsonSource):
    @property
    def environ():
        return json.loads(os.environ.get("SOURCE_2"))

    @classmethod
    def match(cls, href: str):
        href_dict = cls.environ["services"][0]["href"]

        if href_dict["from"] in href:
            return True
        elif href_dict["match"] in href:
            return True

        return False

    @classmethod
    async def __explain_from_creator_list(
        cls, username: str, service: str = "patreon"
    ) -> ExplainedFeed:
        href = cls.environ["creators"]
        response_str = cls.__request_via_random_proxy(href)

        if not response_str:
            # logger.warning(">>>> >>>> EMPTY RESPONSE STR")
            return
        # else:
        #     logger.warning(f">>>> >>>> {response_str=}")

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
                    "href": cls.environ[0]["href"]["from"] + creator["id"],
                    "href_user": "",
                    "private": True,
                    "frequency": "days",
                    "notes": "",
                    "json": {},
                }

    def __init__(self, href: str):
        if os.environ.get("SOURCE_2_FROM") in href:
            self.href = href.replace(
                self.environ[0]["href"]["from"],
                self.environ[0]["href"]["to"],
            )
        elif self.environ[0]["href"]["match"] in href:
            self.href = href
        self.href_original = href

    async def explain(self) -> ExplainedFeed:
        if self.environ[0]["href"]["to"] in self.href:
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
        elif self.environ[0]["href"]["match"] in self.href:
            return await self.__explain_from_creator_list(
                username=self.href.split("/")[-1],
            )
