import logging

from sentry_sdk import capture_event, capture_exception
from sentry_sdk.utils import current_stacktrace


logger = logging.getLogger(__name__)


class Sentry:
    @staticmethod
    def capture_exception(err: Exception) -> None:
        logger.warning(f"SENTRY ERROR: {err}")
        capture_exception(err)

    @staticmethod
    def run_message(message):
        """
        Capture the current stacktrace and send it to Sentry as an
        CapturedStacktrace with stacktrace context.

        Copied from from https://www.bugsink.com/blog/capture-stacktrace-no-exception/
        """
        # with capture_internal_exceptions():  commented out "for now"
        # client_options = sentry_sdk.client.get_options()  "not yet"

        stacktrace = current_stacktrace()
        stacktrace["frames"].pop()  # the present function

        event = {
            "level": "error",
            "exception": {
                "values": [
                    {
                        "mechanism": {
                            "type": "generic",
                            "handled": True
                        },
                        "module": stacktrace["frames"][-1]["module"],
                        "type": "CapturedStacktrace",
                        "value": message,
                        "stacktrace": stacktrace,
                    }
                ]
            }
        }

        logger.warning(f"SENTRY MESSAGE: {message}")
        capture_event(event)
