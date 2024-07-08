import os

from sources.source_json_other import OtherJsonSource


class TwoOtherJsonSource(OtherJsonSource):
    @staticmethod
    def match(href: str):
        if os.environ.get("SOURCE_2_FROM") in href:
            return True

        return False

    @staticmethod
    def prepare_href(href: str) -> str:
        return href.replace(
            os.environ.get("SOURCE_2_FROM"),
            os.environ.get("SOURCE_2_TO"),
        )
