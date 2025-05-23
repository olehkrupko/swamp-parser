import logging
from datetime import datetime
from dateutil import parser, tz  # adding custom timezones

import feedparser

from schemas.feed_explained import ExplainedFeed
from services.capture_exception import CaptureException
from sources.source import Source
from schemas.update import Update


logger = logging.getLogger(__name__)


class RssSource(Source):
    async def parse(self, response_str: str, name_field: str = None) -> list[Update]:
        request = feedparser.parse(response_str)

        results = []
        for each in request["items"]:
            if not each:
                message = f"Feed {self.href=} is empty, skipping"
                CaptureException.run(message)
                continue
            try:
                result_href = each["links"][0]["href"]
            except KeyError:
                CaptureException.run(
                    f"Data missing URL, skipping item {self.href=} {each=}"
                )
                continue

            if name_field:
                name = each[name_field]
            elif each.get("title_detail"):
                name = each["title_detail"]["value"]
            else:
                return ""

            # DATE RESULT: parsing dates
            if "published" in each:
                result_datetime = each["published"]
            elif "delayed" in each:
                result_datetime = each["delayed"]
            elif "updated" in each:
                result_datetime = each["updated"]
            else:
                CaptureException.run("result_datetime broke for feed")

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
                    "name": name,
                    "href": result_href,
                    "datetime": result_datetime,
                }
            )

        return results

    async def explain(self) -> ExplainedFeed:
        data = feedparser.parse(
            await self.request(),
        )

        logger.debug(f"Parsed data: {data}")
        return {
            "title": data["feed"]["title"],
            "href": self.href,
            "href_user": "",
            "private": False,
            "frequency": "hours",
            "notes": "",
            "json": {},
        }
