from fastapi import APIRouter

from runners import object_factory
from responses.PrettyJsonResponse import PrettyJsonResponse
from schemas.feed import ExplainedFeed
from schemas.update import Update


router = APIRouter(
    prefix="/parse",
)


# curl -X GET "http://127.0.0.1:30015/parse/updates?href=https://texty.org.ua/articles/feed.xml"
@router.get("/updates", response_class=PrettyJsonResponse)
async def parse_updates(
    href: str,
) -> list[Update]:
    "Parse one feed by URL."
    results = await parser.parse_href(
        href=href,
    )

    return results


# curl -X GET "http://127.0.0.1:30015/parse/explained?href=https://www.pravda.com.ua/rss/view_mainnews/"
@router.get("/explained", response_class=PrettyJsonResponse)
async def parse_explained(
    href: str,
) -> ExplainedFeed:
    "Get deatails about one feed."
    result = await parser.explain_feed(
        href=href,
    )

    return result
