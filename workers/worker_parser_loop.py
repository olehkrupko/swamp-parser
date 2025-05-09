import asyncio
import logging
from os import getenv

from runners.consumer import Consumer
from services.capture_exception import CaptureException


logger = logging.getLogger(__name__)


class ParserLoopWorker:
    name = "Worker: parser loop"

    async def start():
        AUTOINGEST_ENABLED = bool(getenv("AUTOINGEST_ENABLED", "false"))

        if AUTOINGEST_ENABLED is False:
            logger.warning("ParserLoopWorker: Disabled")
            return
        elif AUTOINGEST_ENABLED is not True:
            logger.warning("ParserLoopWorker: Wrong AUTOINGEST_ENABLED value")
            logger.warning(f"{type(getenv('AUTOINGEST_ENABLED'))} - {getenv('AUTOINGEST_ENABLED')=}")
            return

        logger.warning("ParserLoopWorker: Enabled")
        while True:
            # waiting before run to allow other services some time to start
            await asyncio.sleep(3 * 60)
            try:
                await Consumer.runner()
            except Exception as e:
                CaptureException.run(e)
                logger.error(f"ERROR: {e}")
