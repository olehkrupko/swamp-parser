import aiohttp
from datetime import datetime


class Source:
    datetime_format = ""

    @classmethod
    def strptime(cls, datetime_string):
        return datetime.strptime(
            datetime_string,
            cls.datetime_format,
        )

    async def request(href, headers={}):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                href,
                headers=headers,
            ) as response:
                return await response.read()
