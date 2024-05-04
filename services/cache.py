import os
from datetime import datetime, timedelta

import redis.asyncio as redis


class Cache:
    @staticmethod
    def key_from_href(href: str) -> str:
        return f"swamp-parser:request:{href}"

    @staticmethod
    def timeout() -> datetime:
        return datetime.now() + timedelta(days=7)

    @classmethod
    async def get(cls, href: str) -> str:
        r = await redis.from_url(os.environ["REDIS"], decode_responses=True)
        async with r.pipeline(transaction=True) as pipe:
            values = await pipe.get(cls.key_from_href(href)).execute()
            # result is a list
            return values[0]

    @classmethod
    async def set(cls, href: str, value: str):
        r = await redis.from_url(os.environ["REDIS"], decode_responses=True)
        async with r.pipeline(transaction=True) as pipe:
            await pipe.set(cls.key_from_href(href), str(value)).expireat(
                cls.key_from_href(href), cls.timeout()
            ).execute()
