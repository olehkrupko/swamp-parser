from fastapi import APIRouter

from parsers import parser
from responses.PrettyJsonResponse import PrettyJsonResponse
from schemas.update import Update


router = APIRouter(
    prefix="/parse",
)


# curl -X GET "http://127.0.0.1:30015/parse?href=https://texty.org.ua/articles/feed.xml"
@router.get("/", response_class=PrettyJsonResponse)
async def parse_async(
    href: str,
) -> list[Update]:
    "Parse one feed by URL."
    results = await parser.parse_href(
        href=href,
    )

    return results
