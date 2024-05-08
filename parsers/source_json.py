import json

from parsers.source import Source
from schemas.update import Update


class JsonSource(Source):
    @classmethod
    async def parse(cls, response_str: str) -> list[Update]:
        response_data = json.loads(response_str)

        return response_data
