from fastapi import APIRouter

from responses.PrettyJsonResponse import PrettyJsonResponse
from runner.runner import runner as runner_func
from runner.runner_async import runner as runner_async_func


router = APIRouter(
    prefix="/runner",
)


# DEPRECATED
@router.get("/", response_class=PrettyJsonResponse)
def run() -> dict:
    "Parse all feeds."
    return runner_func()


@router.get("/async/", response_class=PrettyJsonResponse)
async def run_async() -> dict:
    "Parse multiple feeds. Asynchronously."
    return await runner_async_func()


# curl -X GET "http://127.0.0.1:30015/runner/ingest/?feed_id=5734"
@router.get("/ingest/", response_class=PrettyJsonResponse)
async def run_by_id(feed_id: int) -> dict:
    "Parse one feed by URL and send it to DB"
    return await runner_async_func(feed_ids=[feed_id])
