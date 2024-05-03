import feedparser
from datetime import datetime
from dateutil import parser, tz  # adding custom timezones

from parsers.source import Source
from schemas.update import Update


class RssSource(Source):
    @staticmethod
    def each_name(each) -> str:
        if each.get("title_detail"):
            return each["title_detail"]["value"]

        return ""

    async def parse(self, response_str: str) -> list[Update]:
        request = feedparser.parse(response_str)

        results = []
        for each in request["items"]:
            if not each:
                message = f"Feed {self.href=} is empty, skipping"
                self.capture_exception(message)
                continue
            try:
                result_href = each["links"][0]["href"]
            except KeyError:
                self.capture_exception(
                    f"Data missing URL, skipping item {self.href=} {each=}"
                )
                continue

            # DATE RESULT: parsing dates
            if "published" in each:
                result_datetime = each["published"]
            elif "delayed" in each:
                result_datetime = each["delayed"]
            elif "updated" in each:
                result_datetime = each["updated"]
            else:
                self.capture_exception("result_datetime broke for feed")

            tzinfos = {
                "PDT": tz.gettz("America/Los_Angeles"),
                "PST": tz.gettz("America/Juneau"),
            }
            if result_datetime.isdigit():
                result_datetime = datetime.utcfromtimestamp(int(result_datetime))
            elif not isinstance(result_datetime, datetime):
                result_datetime = parser.parse(
                    result_datetime,
                    tzinfos=tzinfos,
                )

            # APPEND RESULT
            results.append(
                {
                    "name": self.each_name(each),
                    "href": result_href,
                    "datetime": result_datetime,
                }
            )

        return results
