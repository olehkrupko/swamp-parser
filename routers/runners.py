from fastapi import APIRouter

from responses.PrettyJsonResponse import PrettyJsonResponse
from runner.runner import runner as runner_func
from runner.runner_async import runner as runner_async_func


router = APIRouter(
    prefix="/runner",
)


# DEPRECATED
@router.get("/", response_class=PrettyJsonResponse)
def runner() -> dict:
    "Parse all feeds."
    return runner_func()


@router.get("/async", response_class=PrettyJsonResponse)
async def runner_async() -> dict:
    "Parse multiple feeds. Asynchronously."
    return await runner_async_func()
