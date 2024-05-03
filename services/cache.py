import os
from datetime import datetime, timedelta

import redis.asyncio as redis


class Cache:
    @staticmethod
    def url(self):
        return f"swamp-parser:request:{self.href}"

    @staticmethod
    def timeout():
        return datetime.now() + timedelta(days=7)

    @classmethod
    async def get(cls):
        r = await redis.from_url(os.environ["REDIS"])
        async with r.pipeline(transaction=True) as pipe:
            return await pipe.get(cls.cache_url())

    @classmethod
    async def set(cls, value: str):
        r = await redis.from_url(os.environ["REDIS"])
        async with r.pipeline(transaction=True) as pipe:
            await pipe.set(cls.cache_url(), value)
            pipe.expireat(cls.cache_url(), cls.cache_timeout())
