import logging
import os

from sources.source_json_other import OtherJsonSource


logger = logging.getLogger(__name__)


class TwoOtherJsonSource(OtherJsonSource):
    @staticmethod
    def match(href: str):
        if os.environ.get("SOURCE_2_FROM") in href:
            return True

        return False

    def __init__(self, href: str):
        self.href = href.replace(
            os.environ.get("SOURCE_2_FROM"),
            os.environ.get("SOURCE_2_TO"),
        )
        self.href_original = href
