import asyncio
import logging
import os

import aiohttp
from services.capture_exception import CaptureException

from runners import parsers
from schemas.feed import Feed
from services.swamp import Swamp


logger = logging.getLogger(__name__)


class Consumer:
    # not actually a consumer pattern as there is no global resource to share

    @staticmethod
    async def task(feed: Feed):
        try:
            async with connection_semaphore:
                updates = []
                for each in await parsers.updates(feed["href"]):
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
            # import traceback
            # traceback.print_exc()  # prints error as usual
            e.args = (feed["href"], *e.args)
            raise e

    @classmethod
    async def runner(cls, feed_ids: list[int] = None):
        logger.warning("Consumer.__init__(): Starting...")
        global connection_semaphore, push_semaphore
        connection_semaphore = asyncio.Semaphore(
            int(os.environ.get("AIOHTTP_SEMAPHORE")),
        )
        # semaphore 1 for ingestion of items one by one, so feeds don't really mix with each other
        push_semaphore = asyncio.Semaphore(1)

        # run coroutines
        try:
            if feed_ids is None:
                feeds = await Swamp.get_feeds()
            else:
                feeds = [await Swamp.get_feed(x) for x in feed_ids]
        except aiohttp.client_exceptions.ClientConnectorError as e:
            # triggered by swamp-api not being up on startup
            # skipping this error so it can work properly next time instead of failing
            CaptureException.run(e)
            logger.error(f"ERROR: {e}")
            feeds = []

        coroutines = []
        for feed in feeds:
            coroutines.append(
                asyncio.Task(
                    cls.task(feed),
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
            CaptureException.run(err)
        errors = list(map(lambda x: f"{ type(x) }: {x}", errors))
        results = list(filter(lambda x: isinstance(x, dict), results))
        updates_new = sum([x["updates_new"] for x in results])

        # print and return results
        if errors:
            logger.warning(f"Consumer.__init__(): {errors=}")
        logger.warning(
            f"Consumer.__init__(): {len(feeds)=}, {updates_new=}, {len(errors)=}"
        )
        if updates_new > 0:
            updates_new__gt_zero = list(filter(lambda x: x["updates_new"] > 0, results))
            logger.warning(f"Consumer.__init__(): updates_new>0={updates_new__gt_zero}")
        logger.warning("Consumer.__init__(): Returning...")
        logger.warning("")
        return {
            "errors": errors,
            "results": results,
            "updates_new": updates_new,
        }
