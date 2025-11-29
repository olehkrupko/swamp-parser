import logging

from sentry_sdk import capture_event, capture_exception
from sentry_sdk.utils import current_stacktrace


logger = logging.getLogger(__name__)


class CaptureException:
    @staticmethod
    def run(err: Exception) -> None:
        logger.warning(f"ERROR: {err}")
        capture_exception(err)


    # from https://www.bugsink.com/blog/capture-stacktrace-no-exception/
    def run_message(message):
        """
        Capture the current stacktrace and send it to Sentry as an
        CapturedStacktrace with stacktrace context.
        """
        # with capture_internal_exceptions():  commented out "for now"
        # client_options = sentry_sdk.client.get_options()  "not yet"

        stacktrace = current_stacktrace()
        stacktrace["frames"].pop()  # the present function

        event = {
            'level': 'error',
            'exception': {
                'values': [{
                    'mechanism': {
                        'type': 'generic',
                        'handled': True
                    },
                    'module': stacktrace["frames"][-1]["module"],
                    'type': 'CapturedStacktrace',
                    'value': message,
                    'stacktrace': stacktrace,
                }]
            }
        }
        capture_event(event)
