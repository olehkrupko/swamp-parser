import asyncio
from contextlib import asynccontextmanager
from os import getenv

from fastapi import FastAPI
import sentry_sdk

from routers import consumers, parsers, tests
from workers.worker_parser_loop import ParserLoopWorker


sentry_sdk.init(
    dsn=getenv("SENTRY_SDK_DSN"),
    # Add data like request headers and IP for users, if applicable;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # # Set traces_sample_rate to 1.0 to capture 100%
    # # of transactions for tracing.
    # traces_sample_rate=1.0,
    # # To collect profiles for all profile sessions,
    # # set `profile_session_sample_rate` to 1.0.
    # profile_session_sample_rate=1.0,
    # # Profiles will be automatically collected while
    # # there is an active span.
    # profile_lifecycle="trace",
    # # Enable logs to be sent to Sentry
    # enable_logs=True,
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
