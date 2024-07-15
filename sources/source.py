import aiohttp
import random
import string
from datetime import datetime

from sentry_sdk import capture_exception as sentry_capture_exception

from schemas.update import Update


class Source:
    datetime_format = None

    @classmethod
    def strptime(cls, datetime_string: str) -> datetime:
        if cls.datetime_format is None:
            raise AttributeError("You need to assign cls.datetime_format != None")

        return datetime.strptime(
            datetime_string,
            cls.datetime_format,
        )

    def __init__(self, href: str):
        self.href = href
        self.href_original = href

    async def request(self) -> str:
        # avoiding blocks
        referer_domain = "".join(random.choices(string.ascii_letters, k=16))
        headers = {
            # 'user-agent': feed.UserAgent_random().strip(),
            "referer": f"https://www.{ referer_domain }.com/?q={ self.href }"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.href,
                headers=headers,
                verify_ssl=False,
            ) as response:
                # ssl._create_default_https_context = getattr(
                #     ssl, "_create_unverified_context"
                # )
                return await response.read()

    @classmethod
    async def parse(cls, each):
        raise NotImplementedError("Expected to be implemented in child classes")

    async def run(self) -> list[Update]:
        # receive data
        response_str = await self.request()

        # process data
        results = await self.parse(response_str=response_str)

        return results

    def capture_exception(msg: str):
        sentry_capture_exception(msg)

    async def explain(self) -> None:
        raise NotImplementedError
