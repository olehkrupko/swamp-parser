import os
from datetime import datetime, timedelta

import redis.asyncio as redis


class Cache:
    def url(self):
        return f"swamp-parser:request:{self.href}"

    def timeout():
        return datetime.now() + timedelta(days=7)

    async def get(self):
        r = await redis.from_url(os.environ["REDIS"])
        async with r.pipeline(transaction=True) as pipe:
            return await pipe.get(self.cache_url())

    async def set(self, value: str):
        r = await redis.from_url(os.environ["REDIS"])
        async with r.pipeline(transaction=True) as pipe:
            await pipe.set(self.cache_url(), value)
            pipe.expireat(self.cache_url(), self.cache_timeout())
