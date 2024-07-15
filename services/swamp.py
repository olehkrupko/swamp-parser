import aiohttp
import os

from schemas.feed import Feed


class Swamp:
    """
    Swamp class for swamp-api

    Contains methods used to send requests to swamp-api
    """

    @staticmethod
    async def get_feeds() -> list[Feed]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ os.environ['SWAMP_API'] }/feeds/?requires_update=true"
            ) as response:
                return [Feed.from_full(x) for x in await response.json()]

    @staticmethod
    async def get_feed(feed_id: int) -> Feed:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ os.environ['SWAMP_API'] }/feeds/{ feed_id }"
            ) as response:
                return Feed.from_full(await response.json())
