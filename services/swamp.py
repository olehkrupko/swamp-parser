import aiohttp
import os

from schemas.feed import Feed


class Swamp:
    # methods for swamp-api usage

    @classmethod
    async def get_feeds(cls) -> list[Feed]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ os.environ['SWAMP_API'] }/feeds/?requires_update=true"
            ) as response:
                return [cls.from_full(x) for x in await response.json()]

    @classmethod
    async def get_feed(cls, feed_id: int) -> Feed:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ os.environ['SWAMP_API'] }/feeds/{ feed_id }"
            ) as response:
                return cls.from_full(await response.json())
