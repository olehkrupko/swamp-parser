from fastapi import APIRouter

from parsers import parser_async
from responses.PrettyJsonResponse import PrettyJsonResponse
from schemas.feed import ExplainedFeed


router = APIRouter(
    prefix="/explain",
)


# curl -X GET "http://127.0.0.1:30015/explain/?href=https://www.pravda.com.ua/rss/view_mainnews/"
@router.get("/", response_class=PrettyJsonResponse)
async def explain_feed(
    href: str,
) -> ExplainedFeed:
    "Get deatails about one feed."
    result = await parser_async.explain_feed(
        href=href,
    )

    return result
