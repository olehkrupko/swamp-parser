from datetime import datetime
from enum import Enum

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field

import parsers.base as parser_base


app = FastAPI(
    title="swamp-parser",
    description="Parser micro-service for Swamp project ([swamp-api](https://github.com/olehkrupko/swamp-api), to be exact)",
    version="0.1",
)


#########
# SCHEMAS START
#########


class Frequency(Enum):
    """Frequency of Feed updates"""

    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"
    # disabled:
    NEVER = "never"


class Update(BaseModel):
    name: str
    href: str
    datetime: datetime


#########
# SCHEMAS END
#########


@app.get("/")
def index() -> str:
    return "Base URL, nothing to see there"


# python3
# import requests
# requests.post("http://127.0.0.1:30015/parse", json={"href": "https://texty.org.ua/articles/feed.xml"}).text
@app.post("/parse")
def parse(
    payload: dict[str, str | bool]
) -> list[Update]:
    "Parse one feed by URL."
    results = parser_base.parse_href(
        href=payload['href'],
    )

    return results


# @app.post("/runner")
# def runner():
#     "Parse multiple feeds"


@app.post("/parse/async")
async def parse_async(
    payload: dict[str, str | bool]
) -> list[Update]:
    "Parse one feed by URL. Asynchronously."
    results = await parser_base_async.parse_href(
        href=payload['href'],
    )

    return results
