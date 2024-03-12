from fastapi import APIRouter

from responses.PrettyJSONResponse import PrettyJSONResponse
from runner.runner import runner as runner_func
from runner.runner_async import runner as runner_async_func


router = APIRouter(
    prefix="/runner",
)


# DEPRECATED
@router.get("/", response_class=PrettyJSONResponse)
def runner() -> dict:
    "Parse all feeds."
    return runner_func()


@router.get("/async", response_class=PrettyJSONResponse)
async def runner_async() -> dict:
    "Parse multiple feeds. Asynchronously."
    return await runner_async_func()
