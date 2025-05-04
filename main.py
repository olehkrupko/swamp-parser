import asyncio
import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI

from routers import consumers, parsers, tests
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
    asyncio.create_task(
        ParserLoopWorker.start(),
        name=ParserLoopWorker.name,
    )

    yield
    # run on shutdown


app = FastAPI(
    title="swamp-parser",
    description="""
        GitHub: [swamp-parser](https://github.com/olehkrupko/swamp-parser)
        Is one of swamp services, related to [swamp-api](https://github.com/olehkrupko/swamp-api)
    """,
    version="V3",
    lifespan=lifespan,
)
app.include_router(consumers.router)  # not in use for now
app.include_router(parsers.router)
app.include_router(tests.router)
