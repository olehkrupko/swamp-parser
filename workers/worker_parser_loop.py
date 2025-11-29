import asyncio
import logging
from os import getenv

from runners.consumer import Consumer
from services.sentry import Sentry


logger = logging.getLogger(__name__)


class ParserLoopWorker:
    name = "Worker: parser loop"

    async def start():
        if getenv("AUTOINGEST") != "enabled":
            logger.warning(f"ParserLoopWorker: Disabled ({ getenv('AUTOINGEST')= })")
            return

        logger.warning("ParserLoopWorker: Enabled")
        # initial delay of 1h to allow other services to start
        await asyncio.sleep(1 * 60 * 60)

        while True:
            try:
                await Consumer.runner()
            except Exception as err:
                Sentry.capture_exception(err)
            finally:
                # waiting before between runs
                await asyncio.sleep(3 * 60)
