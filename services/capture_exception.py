import logging

from sentry_sdk import capture_exception


logger = logging.getLogger(__name__)


class CaptureException:
    @staticmethod
    def run(msg: str) -> None:
        logger.debug(f"Exception captured: {msg}")
        capture_exception(msg)
