import asyncio
import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI

from routers import parsers, runners, tests
from workers.worker_parser_loop import ParserLoopWorker


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # run on startup
    global connection_semaphore, push_semaphore
    connection_semaphore = asyncio.Semaphore(
        int(os.environ.get("AIOHTTP_SEMAPHORE")),
    )
    # semaphore 1 for ingestion of items one by one, so feeds don't really mix with each other
    push_semaphore = asyncio.Semaphore(1)
    asyncio.create_task(
        ParserLoopWorker.start(),
        name=ParserLoopWorker.name,
    )

    yield
    # run on shutdown


URL = "[swamp-api](https://github.com/olehkrupko/swamp-api)"
app = FastAPI(
    title="swamp-parser",
    description=f"Parser micro-service for Swamp project ({ URL }, to be exact)",
    version="2.3",  # Issue 10: fast-api routes
    lifespan=lifespan,
)
app.include_router(parsers.router)
app.include_router(runners.router)
app.include_router(tests.router)
