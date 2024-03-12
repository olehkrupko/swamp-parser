import time

from fastapi import APIRouter

from responses.PrettyJsonResponse import PrettyJsonResponse
from runner.runner import runner as runner_func
from runner.runner_async import runner as runner_async_func


router = APIRouter(
    prefix="/tests",
)

# DEPRECATED
@router.get("/", response_class=PrettyJsonResponse)
async def test() -> dict:
    "Parse multiple feeds."
    t_start_total = time.perf_counter()

    t_start = time.perf_counter()
    result = runner_func()
    t_end = time.perf_counter()
    t_sync = t_end - t_start

    t_start = time.perf_counter()
    result_async = await runner_async_func()
    t_end = time.perf_counter()
    t_async = t_end - t_start

    # how quicker async is
    # measured in seconds
    improvement = t_sync - t_async

    t_end_total = time.perf_counter()
    t_total = t_end_total - t_start_total

    return {
        "async_improvement": round(improvement, 10),
        "total": round(t_total, 10),
        "parser_base": {
            "result": result,
            "result_len": len(result),
            "time": round(t_sync, 2),
        },
        "parser_async": {
            "result": result_async,
            "result_len": len(result_async),
            "time": round(t_async, 2),
        },
    }
