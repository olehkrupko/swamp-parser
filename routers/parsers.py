from fastapi import APIRouter

from parsers import parser as parser_base
from parsers import parser_async
from responses.PrettyJsonResponse import PrettyJsonResponse
from schemas.update import Update


router = APIRouter(
    prefix="/parse",
)


# DEPRECATED
# python3
# import requests
# requests.get("http://127.0.0.1:30015/parse?href=https://texty.org.ua/articles/feed.xml").text
@router.get("/", response_class=PrettyJsonResponse)
def parse(
    href: str,
) -> list[Update]:
    "Parse one feed by URL."
    return parser_base.parse_href(
        href=href,
    )


# python3
# import requests
# requests.get("http://127.0.0.1:30015/parse/async?href=https://texty.org.ua/articles/feed.xml").text
@router.get("/async", response_class=PrettyJsonResponse)
async def parse_async(
    href: str,
) -> list[Update]:
    "Parse one feed by URL. Asynchronously."
    results = await parser_async.parse_href(
        href=href,
    )

    return results
