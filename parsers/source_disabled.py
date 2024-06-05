from parsers.source import Source


class DisabledSource(Source):
    async def run(self) -> list:
        return []
