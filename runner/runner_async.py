import asyncio
import json
import os

import aiohttp
from sentry_sdk import capture_exception

import parsers.parser_async as parser_async


async def task(feed):
    async with connection_semaphore:
        updates = []
        for each in await parser_async.parse_href(feed["href"]):
            each["datetime"] = each["datetime"].isoformat()
            updates.append(each)

    async with push_semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{ os.environ['SWAMP_API'] }/feeds/{ feed['_id'] }/",
                json=updates,
            ) as response:
                updates = await response.json()

                print(f"Feed { feed['title'] }, parsed { len(updates) } updates to queue")
                return {
                    "title": feed["title"],
                    "updates_new": len(updates),
                }


async def runner():
    print("runner(): Starting...")
    global connection_semaphore, push_semaphore
    connection_semaphore = asyncio.Semaphore(
        int(os.environ.get("AIOHTTP_SEMAPHORE")),
    )
    # semaphore 1 for ingestion of items one by one, so feeds don't really mix wit each other
    push_semaphore = asyncio.Semaphore(1)

    # run coroutines
    coroutines = []
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{ os.environ['SWAMP_API'] }/feeds/?requires_update=true"
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
    results = await asyncio.gather(
        *coroutines,
        return_exceptions=True,
    )

    # prepare results
    errors = list(filter(lambda x: not isinstance(x, dict), results))
    for err in errors:
        capture_exception(err)
        # raise err
        print(1, err)
    # errors = map(lambda x: str(x), errors)
    errors = map(lambda x: str(type(x)), errors)
    results = list(filter(lambda x: isinstance(x, dict), results))

    print('>>>>', list(filter(lambda x: x["updates_new"] > 0, results)))
    return {
        "results": results,
        "errors": errors,
        "updates_new": sum([x["updates_new"] for x in results]),
    }
