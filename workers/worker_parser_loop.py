import asyncio
import logging
import os

from runners.consumer import Consumer
from services.capture_exception import CaptureException


logger = logging.getLogger(__name__)


class ParserLoopWorker:
    name = "Worker: parser loop"

    async def start():
        if os.environ.get("ALLOW_PARSER_LOOP", False) is False:
            logger.warning("ParserLoopWorker: Disabled")
            return
        elif os.environ.get("ALLOW_PARSER_LOOP", False) is not True:
            logger.warning("ParserLoopWorker: Wrong ALLOW_PARSER_LOOP value")
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
