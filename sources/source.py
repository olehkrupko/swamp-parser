import aiohttp
import logging
import os
import random
import string
from datetime import datetime

from aiohttp_socks import ProxyType, ProxyConnector
from sentry_sdk import capture_exception as sentry_capture_exception

from schemas.update import Update
from services.cache import Cache


logger = logging.getLogger(__name__)


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
        if os.environ["ALLOW_CACHE"] == "true":
            cached_value = await Cache.get(
                type="request",
                href=self.href,
            )
            if cached_value is not None:
                logger.debug(f"Successful cache retrieval for {self.href=}")
                return cached_value

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
                result = await response.read()
                if os.environ["ALLOW_CACHE"] == "true":
                    await Cache.set(
                        type="request",
                        href=self.href,
                        timeout={"seconds": 15},
                        value=result,
                    )
                return result

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

    @staticmethod
    async def __request_via_random_proxy(href, max_attempts=100):
        proxy_list = []
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/refs/heads/master/http.txt",
            ) as response:
                response_str = await response.read()
                proxy_list = response_str.decode("utf-8").split("\n")
                # logger.warning(f">>>> >>>> {type(proxy_list)} {len(proxy_list)}")

        if proxy_list:
            for proxy in random.choices(proxy_list, k=max_attempts):
                connector = ProxyConnector(
                    proxy_type=ProxyType.HTTP,
                    host=proxy.split(":")[0],
                    port=int(proxy.split(":")[1]),
                )

                try:
                    async with aiohttp.ClientSession(connector=connector) as session:
                        async with session.get(
                            href,
                        ) as response:
                            return await response.read()
                except Exception as error:
                    logger.warning(f">>>> >>>> FAILURE {error}")
                    pass
        else:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(
                    href,
                ) as response:
                    return await response.read()
