import logging

from sentry_sdk import capture_exception


logger = logging.getLogger(__name__)


class CaptureException:
    @staticmethod
    def run(err: Exception) -> None:
        logger.error(f"ERROR: {err}")
        capture_exception(err)
