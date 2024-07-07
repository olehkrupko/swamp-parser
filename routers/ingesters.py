from fastapi import APIRouter

from responses.PrettyJsonResponse import PrettyJsonResponse
from runner.runner_async import runner


router = APIRouter(
    prefix="/ingest",
)


# curl -X GET "http://127.0.0.1:30015/ingest/"
@router.get("/", response_class=PrettyJsonResponse)
async def run() -> dict:
    "Ingest all feeds that requires an update."
    return await runner()


# curl -X GET "http://127.0.0.1:30015/ingest/5734"
@router.get("/{feed_id}", response_class=PrettyJsonResponse)
async def run_by_id(feed_id: int) -> dict:
    "Ingest one feed by URL."
    return await runner(feed_ids=[feed_id])
