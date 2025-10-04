import json
import logging
from os import getenv

import aiohttp

from schemas.feed_explained import ExplainedFeed
from services.capture_exception import capture_exception
from sources.source_json_other import OtherJsonSource


logger = logging.getLogger(__name__)


class TwoOtherJsonSource(OtherJsonSource):
    environ = json.loads(getenv("SOURCE_2"))

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
        response_str = await cls.request_via_random_proxy(
            href=href,
            headers={"Accept": "text/css"},
        )

        if not response_str:
            raise Exception("No response")

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
                    "title": username + " - " + cls.environ["services"][0]["name"],
                    "href": cls.environ["services"][0]["href"]["from"] + creator["id"],
                    "href_user": "",
                    "private": True,
                    "frequency": "days",
                    "notes": "",
                    "json": {},
                }

        raise Exception("No matching user found")

    def __init__(self, href: str):
        if self.environ["services"][0]["href"]["from"] in href:
            self.href = href.replace(
                self.environ["services"][0]["href"]["from"],
                self.environ["services"][0]["href"]["to"],
            )
        elif self.environ["services"][0]["href"]["match"] in href:
            self.href = href
        self.href_original = href

    async def explain(self) -> ExplainedFeed:
        if self.environ["services"][0]["href"]["to"] in self.href:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.href + "/profile",
                ) as response:
                    data = await response.json()

                    title = data["name"] + " - " + self.environ["services"][0]["name"]

                    return {
                        "title": title,
                        "href": self.href_original,
                        "href_user": "",
                        "private": True,
                        "frequency": "days",
                        "notes": "",
                        "json": {},
                    }
        elif self.environ["services"][0]["href"]["match"] in self.href:
            return await self.__explain_from_creator_list(
                username=self.href.split("/")[-1],
            )
