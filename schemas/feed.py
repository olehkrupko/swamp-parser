import aiohttp
import os
from pydantic import BaseModel
from typing import Self

# from datetime import datetime

# unused
# class FullFeed(BaseModel):
#     _id: int
#     _created: datetime
#     _delayed: datetime
#     title: str
#     href: str
#     href_user: str
#     private: bool
#     frequency: str
#     notes: str
#     json: dict


# feed with unnecessary fields cut off
class Feed(BaseModel):
    _id: int
    title: str  # not REALLY needed
    href: str

    def from_full(full_feed: dict) -> Self:
        return {
            "_id": full_feed["_id"],
            "href": full_feed["href"],
            "title": full_feed["title"],
        }

    @classmethod
    async def get_feeds(cls) -> list[Self]:
        # try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ os.environ['SWAMP_API'] }/feeds/?requires_update=true"
            ) as response:
                return [cls.from_full(x) for x in await response.json()]
        # TODO: remove later if everything is alright
        # except aiohttp.client_exceptions.ClientConnectorError as e:
        #     # seems to be triggered by swamp-api not being up on startup
        #     # is not expected to happen in the future
        #     capture_exception(e)
        #     feeds = []
        #     logger.error(f"ERROR: {e}")

    @classmethod
    async def get_feed(cls, feed_id: int) -> Self:
        # try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ os.environ['SWAMP_API'] }/feeds/{ feed_id }"
            ) as response:
                return cls.from_full(await response.json())
        # TODO: remove later if everything is alright
        # except aiohttp.client_exceptions.ClientConnectorError as e:
        #     # seems to be triggered by swamp-api not being up on startup
        #     # is not expected to happen in the future
        #     capture_exception(e)
        #     feeds = []
        #     logger.error(f"ERROR: {e}")
