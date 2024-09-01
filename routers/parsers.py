import logging
from fastapi import APIRouter

from runners import parsers
from responses.PrettyJsonResponse import PrettyJsonResponse
from schemas.feed_explained import ExplainedFeed
from schemas.update import Update


router = APIRouter(
    prefix="/parse",
)


logger = logging.getLogger(__name__)


# curl -X GET "http://127.0.0.1:30015/parse/updates?href=https://texty.org.ua/articles/feed.xml"
@router.get("/updates", response_class=PrettyJsonResponse)
async def parse_updates(
    href: str,
) -> list[Update]:
    "Parse updates from one feed by URL."
    results = await parsers.updates(
        href=href,
    )

    return results


# curl -X GET "http://127.0.0.1:30015/parse/explained?href=https://texty.org.ua/articles/feed.xml"
@router.get("/explained", response_class=PrettyJsonResponse)
async def parse_explained(
    href: str,
) -> ExplainedFeed:
    "Parse details about one feed."
    result = await parsers.explain(
        href=href,
    )

    return result
