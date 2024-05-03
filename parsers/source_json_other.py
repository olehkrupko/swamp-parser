from parsers.source_json import JsonSource
from schemas.update import Update


class OtherJsonSource(JsonSource):
    datetime_format = "%Y-%m-%dT%H:%M:%S"

    @classmethod
    def parse(cls, response_str: str) -> list[Update]:
        results = []

        for each in super().parse(response_str=response_str):
            datetime_string = each["published"]
            if not datetime_string:
                datetime_string = each["added"]

            results.append(
                {
                    "name": each["title"],  # longer alternative: each["content"]
                    "href": each["id"],
                    "datetime": cls.strptime(datetime_string),
                }
            )
