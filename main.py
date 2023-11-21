import time
from datetime import datetime
from enum import Enum

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field

import parsers.base as parser_base
import parsers.base_async as parser_base_async
from runner.runner import runner as runner_func
from runner.runner_async import runner as runner_async_func


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
# requests.get("http://127.0.0.1:30015/parse?href=https://texty.org.ua/articles/feed.xml").text
@app.get("/parse/")
def parse(
    href: str,
) -> list[Update]:
    "Parse one feed by URL."
    results = parser_base.parse_href(
        href=href,
    )

    return results


# python3
# import requests
# requests.get("http://127.0.0.1:30015/parse/async?href=https://texty.org.ua/articles/feed.xml").text
@app.get("/parse/async/")
async def parse_async(
    href: str,
) -> list[Update]:
    "Parse one feed by URL. Asynchronously."
    results = await parser_base_async.parse_href(
        href=href,
    )

    return results


@app.get("/runner/")
def runner() -> dict:
    "Parse multiple feeds."
    return runner_func()


@app.get("/runner/async/")
async def runner_async() -> dict:
    "Parse multiple feeds. Asynchronously."
    return await runner_async_func()
