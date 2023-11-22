import asyncio
import os
import time

import aiohttp

import parsers.base_async as parser_base_async


async def task(href):
    async with connection_semaphore:
        return await parser_base_async.parse_href(href["href"])


async def runner():
    global connection_semaphore
    connection_semaphore = asyncio.Semaphore(
        int(os.environ.get("AIOHTTP_SEMAPHORE")),
    )

    # run coroutines
    coroutines = []
    async with aiohttp.ClientSession() as session:
        async with session.get(os.environ["SWAMP_API_FEEDS"]) as response:
            feeds = await response.json()

            for feed in feeds:
                coroutines.append(
                    asyncio.Task(
                        task(feed),
                        name=f"parse_async({ feed['title'] })",
                    )
                )

    # Await completion
    # results = await asyncio.gather(*coroutines, return_exceptions=True)
    # return results
    await asyncio.gather(*coroutines, return_exceptions=True)
