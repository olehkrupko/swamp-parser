import asyncio
import os

import aiohttp

import parsers.parser_async as parser_async


async def task(feed):
    async with connection_semaphore:
        updates = await parser_async.parse_href(feed["href"])

    results = []
    async with connection_semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                data=updates,
                f"{ os.environ['SWAMP_API'] }/feeds/{ feed['_id'] }/",
            ) as response:
                updates = await response.json()

                results.append(
                    {
                        "title": feed["title"],
                        "updates": len(updates),
                    }
                )

    return results


async def runner():
    global connection_semaphore
    connection_semaphore = asyncio.Semaphore(
        int(os.environ.get("AIOHTTP_SEMAPHORE")),
    )

    # run coroutines
    coroutines = []
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{ os.environ['SWAMP_API_FEEDS'] }/feeds/?requires_update=true"
        ) as response:
            feeds = await response.json()

            for feed in feeds:
                coroutines.append(
                    asyncio.Task(
                        task(feed),
                        name=f"parse_async({ feed['title'] })",
                    )
                )

    # Await completion
    results = await asyncio.gather(*coroutines, return_exceptions=True)

    return results
