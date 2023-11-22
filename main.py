import time
from datetime import datetime
from enum import Enum

import sentry_sdk
from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Field

import parsers.parser as parser_base
import parsers.parser_async
from responses.PrettyJSONResponse import PrettyJSONResponse
from runner.runner import runner as runner_func
from runner.runner_async import runner as runner_async_func


sentry_sdk.init(
    dsn=os.environ["SENTRY_SDK_DSN"],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)


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
@app.get("/parse/", response_class=PrettyJSONResponse)
def parse(
    href: str,
) -> list[Update]:
    "Parse one feed by URL."
    return parser_base.parse_href(
        href=href,
    )


# python3
# import requests
# requests.get("http://127.0.0.1:30015/parse/async?href=https://texty.org.ua/articles/feed.xml").text
@app.get("/parse/async/", response_class=PrettyJSONResponse)
async def parse_async(
    href: str,
) -> list[Update]:
    "Parse one feed by URL. Asynchronously."
    results = await parser_async.parse_href(
        href=href,
    )

    return results


@app.get("/runner/", response_class=PrettyJSONResponse)
def runner() -> dict:
    "Parse multiple feeds."
    return runner_func()


@app.get("/runner/async/", response_class=PrettyJSONResponse)
async def runner_async() -> dict:
    "Parse multiple feeds. Asynchronously."
    return await runner_async_func()


@app.get("/test/", response_class=PrettyJSONResponse)
async def test() -> dict:
    "Parse multiple feeds."
    t_start_total = time.perf_counter()

    t_start = time.perf_counter()
    result = runner()
    t_end = time.perf_counter()
    t_sync = t_end - t_start

    t_start = time.perf_counter()
    result_async = await runner_async()
    t_end = time.perf_counter()
    t_async = t_end - t_start

    # how quicker async is
    # measured in seconds
    improvement = t_sync - t_async

    t_end_total = time.perf_counter()
    t_total = t_end_total - t_start_total

    return {
        "async_improvement": round(improvement, 10),
        "total": round(t_total, 10),
        "parser_base": {
            "result": result,
            "result_len": len(result),
            "time": round(t_sync, 2),
        },
        "parser_async": {
            "result": result_async,
            "result_len": len(result_async),
            "time": round(t_async, 2),
        },
    }
