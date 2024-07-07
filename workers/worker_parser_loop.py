import asyncio
import logging

from sentry_sdk import capture_exception

from runner.consumer import start


logger = logging.getLogger(__name__)


class ParserLoopWorker:
    name = "Worker: parser loop"

    async def start():
        while True:
            # waiting before run to allow other services some time to start
            await asyncio.sleep(3 * 60)
            try:
                await start()
            except Exception as e:
                capture_exception(e)
                logger.error(f"ERROR: {e}")
