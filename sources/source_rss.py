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
    def strptime(self, datetime_string: str) -> datetime:
        tzinfos = {
            "PDT": tz.gettz("America/Los_Angeles"),
            "PST": tz.gettz("America/Juneau"),
        }

        if datetime_string.isdigit():
            return datetime.fromtimestamp(
                timestamp=int(datetime_string),
                tz=datetime.timezone.utc,
            )
        elif isinstance(datetime_string, datetime):
            raise ValueError(
                f"datetime_string is already a datetime object: {datetime_string}"
            )
        else:
            return parser.parse(
                datetime_string,
                tzinfos=tzinfos,
            )

    async def parse(self, response_str: str, name_field: str = None) -> list[Update]:
        request = feedparser.parse(response_str)

        results = []
        for each in request["items"]:
            if not each:
                CaptureException.run(
                    ValueError(f"Feed {self.href=} is empty, skipping")
                )
                continue
            try:
                result_href = each["links"][0]["href"]
            except KeyError:
                CaptureException.run(
                    KeyError(f"Data missing URL, skipping item {self.href=} {each=}")
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
                result_datetime = self.strptime(each["published"])
            elif "delayed" in each:
                result_datetime = self.strptime(each["delayed"])
            elif "updated" in each:
                result_datetime = self.strptime(each["updated"])
            elif self.datetime_format == "NOW":
                result_datetime = datetime.now()
            else:
                result_datetime = datetime.now()
                CaptureException.run(
                    ValueError("No datetime found, using datetime.now()")
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
