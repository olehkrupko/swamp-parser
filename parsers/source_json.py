import json

from parsers.source import Source


class JsonSource(Source):
    @classmethod
    def _parse_each(cls, each):
        raise NotImplementedError("Expected to be implemented in child classes")

    @classmethod
    def parse(cls, response_str):
        response_data = json.loads(response_str)

        return list(
            map(
                lambda x: cls._parse_each(x),
                response_data,
            )
        )