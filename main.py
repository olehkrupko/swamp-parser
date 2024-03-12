import asyncio
import os

import sentry_sdk
from fastapi import FastAPI

from routers import parsers, runners, tests
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


DEFAULT_RESPONSES = {
    404: {"description": "Not found"},
}
URL = "[swamp-api](https://github.com/olehkrupko/swamp-api)"
app = FastAPI(
    title="swamp-parser",
    description=f"Parser micro-service for Swamp project ({ URL }, to be exact)",
    version="2.3",  # Issue 10: fast-api routes
)
app.include_router(
    parsers.router,
    responses=DEFAULT_RESPONSES,
)
app.include_router(
    runners.router,
    responses=DEFAULT_RESPONSES,
)
app.include_router(
    tests.router,
    responses=DEFAULT_RESPONSES,
)


async def runned_async_schedule():
    while True:
        # waiting before run to allow other services some time to start
        await asyncio.sleep(3 * 60)
        await runner_async_func()


@app.on_event("startup")
def startup_function():
    asyncio.create_task(
        runned_async_schedule(),
        name="Worker: parser loop",
    )
