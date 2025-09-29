import asyncio
import logging
from os import getenv

from runners.consumer import Consumer
from services.capture_exception import CaptureException


logger = logging.getLogger(__name__)


class ParserLoopWorker:
    name = "Worker: parser loop"

    async def start():
        if getenv("AUTOINGEST") != "enabled":
            logger.warning(f"ParserLoopWorker: Disabled ({ getenv('AUTOINGEST')= })")
            return

        logger.warning("ParserLoopWorker: Enabled")
        while True:
            # waiting before run to allow other services some time to start
            await asyncio.sleep(3 * 60)
            try:
                await Consumer.runner()
            except Exception as err:
                CaptureException.run(err)
                logger.error(f"ERROR: {err}")
