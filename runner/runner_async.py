import asyncio
import os

import aiohttp
from sentry_sdk import capture_message

import parsers.parser_async as parser_async


async def task(feed):
    async with connection_semaphore:
        print('>>>>', 0, "receive data")
        updates = []
        for each in await parser_async.parse_href(feed["href"]):
            each["datetime"] = each["datetime"].isoformat()
            updates.append(each)
        print('>>>>', 1, updates)

    async with push_semaphore:
        print('>>>>', 2, "push data")
        params = pika.URLParameters(os.environ["RABBITMQ_CONNECTION_STRING"])
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.basic_publish(
            exchange="swamp",
            routing_key="feed.push",
            body=json.dumps({
                "_id": feed['_id'],
                "updates": updates,
            }),
        )

    print('>>>>', 3, "return data")
    return {
        "title": feed["title"],
        "updates": len(updates),
    }


async def runner():
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
    results = await asyncio.gather(*coroutines, return_exceptions=True)

    # prepare results
    errors = list(filter(lambda x: not isinstance(x, dict), results))
    map(lambda x: capture_message(x), errors)
    errors = map(lambda x: str(x), errors)
    results = list(filter(lambda x: isinstance(x, dict), results))

    return {
        "total_new": sum([x["updates"] for x in results]),
        "results": results,
        "errors": errors,
    }
