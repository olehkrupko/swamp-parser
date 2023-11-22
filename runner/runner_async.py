import asyncio
import os
import time

import aiohttp

import parsers.base_async as parser_base_async


async def task(href):
    async with connection_semaphore:
        updates = await parser_base_async.parse_href(href["href"])

    results = []
    async with connection_semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{ os.environ['SWAMP_API_FEEDS'] }/feeds/{ feed['feed_id'] }/",
                data=updates,
            ) as response:
                new_updates = await response.json()

                results.append(
                    {
                        'title': feed['title'],
                        'new_updates': new_updates,
                    }
                )

    return feeds


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
