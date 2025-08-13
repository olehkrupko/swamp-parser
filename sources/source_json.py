import json
import logging

from schemas.update import Update
from sources.source import Source


logger = logging.getLogger(__name__)


class JsonSource(Source):
    @classmethod
    async def parse(cls, response_str: str) -> list[Update]:
        response_data = json.loads(response_str)

        return response_data
