import os
from datetime import datetime, timedelta

import redis.asyncio as redis


class Cache:
    @staticmethod
    def key(href: str) -> str:
        return f"swamp-parser:request:{href}"

    @staticmethod
    def timeout() -> datetime:
        return datetime.now() + timedelta(days=7)

    @classmethod
    async def get(cls, href: str) -> str:
        r = await redis.from_url(os.environ["REDIS"])
        async with r.pipeline(transaction=True) as pipe:
            return await pipe.get(cls.key(href))

    @classmethod
    async def set(cls, href: str, value: str):
        r = await redis.from_url(os.environ["REDIS"])
        async with r.pipeline(transaction=True) as pipe:
            await pipe.set(cls.key(href), value)
            pipe.expireat(cls.key(href), cls.cache_timeout())
