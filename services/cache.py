import os
from datetime import datetime, timedelta

import redis.asyncio as redis


class Cache:
    @staticmethod
    def key_from_href(type: str, href: str) -> str:
        return f"swamp-parser:{type}:{href}"

    @staticmethod
    def timeout(timeout: dict) -> datetime:
        return datetime.now() + timedelta(**timeout)

    @classmethod
    async def get(cls, type: str, href: str) -> str:
        r = await redis.from_url(os.environ["REDIS"], decode_responses=True)
        async with r.pipeline(transaction=True) as pipe:
            values = await pipe.get(cls.key_from_href(type=type, href=href)).execute()
            # result is a list, but we need only one item
            return values[0]

    @classmethod
    async def set(cls, type: str, href: str, value: str, timeout: dict):
        r = await redis.from_url(os.environ["REDIS"], decode_responses=True)
        async with r.pipeline(transaction=True) as pipe:
            await pipe.set(
                cls.key_from_href(type=type, href=href),
                str(value),
            ).expireat(
                cls.key_from_href(type=type, href=href),
                cls.timeout(timeout=timeout),
            ).execute()
