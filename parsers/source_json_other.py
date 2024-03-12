import json

from parsers.source import Source


class OtherJsonSource(Source):
    datetime_format = "%Y-%m-%dT%H:%M:%S"

    @classmethod
    def _parse_each(cls, each):
        return {
            "name": each["title"],  # longer alternative: each["content"]
            "href": each["id"],
            "datetime": cls.strptime(each["published"]),
        }

    @classmethod
    def parse(cls, response_str):
        response_data = json.loads(response_str)

        return list(
            map(
                lambda x: cls._parse_each(x),
                response_data,
            )
        )
