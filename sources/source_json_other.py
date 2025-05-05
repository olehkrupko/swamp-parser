from schemas.update import Update
from sources.source_json import JsonSource


class OtherJsonSource(JsonSource):
    datetime_format = "%Y-%m-%dT%H:%M:%S"

    async def request(self):
        return await super().request_via_random_proxy(href=self.href)

    async def parse(self, response_str: str) -> list[Update]:
        results = []

        for each in await super().parse(response_str=response_str):
            datetime_string = each["published"]
            if not datetime_string:
                datetime_string = each["added"]

            results.append(
                {
                    "name": each["title"],  # longer alternative: each["content"]
                    "href": f"{ self.href.replace('/api/v1', '') }/post/{ each['id'] }",
                    "datetime": self.strptime(datetime_string),
                }
            )

        return results
