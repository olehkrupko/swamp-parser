import asyncio
import logging
import os

import aiohttp
from sentry_sdk import capture_exception

import parsers.parser_async as parser_async
from schemas.feed import Feed


logger = logging.getLogger(__name__)


async def task(feed: Feed):
    try:
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

                    return {
                        "title": feed["title"],
                        "updates_new": len(updates),
                    }
    except Exception as e:
        # Inject feed URLs to parsing errors
        raise type(e)(f"{feed['href']}: {str(e)}")


async def runner():
    logger.warning("runner(): Starting...")
    global connection_semaphore, push_semaphore
    connection_semaphore = asyncio.Semaphore(
        int(os.environ.get("AIOHTTP_SEMAPHORE")),
    )
    # semaphore 1 for ingestion of items one by one, so feeds don't really mix with each other
    push_semaphore = asyncio.Semaphore(1)

    # run coroutines
    coroutines = []
    for feed in await Feed.get_feeds():
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
    errors = list(map(lambda x: f"{ type(x) }: {x}", errors))
    results = list(filter(lambda x: isinstance(x, dict), results))
    updates_new = sum([x["updates_new"] for x in results])

    # print and return results
    if errors:
        logger.warning(f"runner(): {errors=}")
    logger.warning(f"runner(): {len(feeds)=}, {updates_new=}, {len(errors)=}")
    if updates_new > 0:
        updates_new__gt_zero = list(filter(lambda x: x["updates_new"] > 0, results))
        logger.warning(f"runner(): updates_new>0={updates_new__gt_zero}")
    logger.warning("runner(): Returning...")
    logger.warning("")
    return {
        "errors": errors,
        "results": results,
        "updates_new": updates_new,
    }
