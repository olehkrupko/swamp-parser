import asyncio

from runner.runner_async import runner as runner_async_func


class ParserLoopWorker:
    name = "Worker: parser loop"

    async def start():
        while True:
            # waiting before run to allow other services some time to start
            await asyncio.sleep(3 * 60)
            await runner_async_func()
