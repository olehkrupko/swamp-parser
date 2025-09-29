import logging
from fastapi import APIRouter

from responses.PrettyJsonResponse import PrettyJsonResponse


router = APIRouter(
    prefix="/test",
)


logger = logging.getLogger(__name__)


# # curl -X GET "http://127.0.0.1:34002/test/healthcheck"
@router.get("/healthcheck", response_class=PrettyJsonResponse)
async def test_healthcheck() -> bool:
    "Return True if system is at least a bit responsive."
    return True
