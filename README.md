# Swamp Parser

This is parsing back-end part of Swamp project which makes actual work of parsing feeds for updates. If you can't destroy [FOMO](https://en.wikipedia.org/wiki/Fear_of_missing_out) — you can conquer it!

Made using FastAPI.

## Available workers

### Worker: parser loop
**Description**: asyncio coroutine run as task on FastAPI startup event.
**Logic**: Wait 3m, parse all feeds that require update provided by `swamp-api` and repeat forever.

## Available routes

| **URL**        | **Description**                           |
| ---            | ---                                       |
| /parse/        | Parse one URL.                            |
| /parse/async/  | Parse one URL asynchronously.             |
| /runner/       | Run non-async runner.                     |
| /runner/async/ | Run async runner.                         |
| /tests/        | Test-compare async and non-async runners. |
