import aiohttp
import random
import string
from datetime import datetime

from sentry_sdk import capture_exception as sentry_capture_exception


class Source:
    datetime_format = ""

    @classmethod
    def strptime(cls, datetime_string: str):
        return datetime.strptime(
            datetime_string,
            cls.datetime_format,
        )

    # def prepare_href(href):
    #     return href.replace(
    #         os.environ.get("SOURCE_1_FROM"),
    #         os.environ.get("SOURCE_1_TO"),
    #     )

    @classmethod
    async def parse(cls, each):
        raise NotImplementedError("Expected to be implemented in child classes")

    # @classmethod
    # def parse_each(cls, each):
    #     raise NotImplementedError("Expected to be implemented in child classes")

    async def request(self, href):
        # avoiding blocks
        referer_domain = "".join(random.choices(string.ascii_letters, k=16))
        headers = {
            # 'user-agent': feed.UserAgent_random().strip(),
            "referer": f"https://www.{ referer_domain }.com/?q={ href }"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                href,
                headers=headers,
                verify_ssl=False,
            ) as response:
                # ssl._create_default_https_context = getattr(
                #     ssl, "_create_unverified_context"
                # )
                return await response.read()

    def __init__(
        self,
        href: str,
    ):
        # prepare URL
        if hasattr(self, "prepare_href"):
            href = self.prepare_href(href)

        self.href = href

    async def run(self):
        # receive data
        response_str = await self.request(href=self.href)

        # process data
        results = await self.parse(response_str=response_str)
        if hasattr(self, "parse_each"):
            results = [self.parse_each(x) for x in results]

        return results

    def capture_exception(msg: str):
        sentry_capture_exception(msg)
