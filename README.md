# Swamp Parser

This is parsing back-end part of Swamp project which makes actual work of parsing feeds for updates. If you can't destroy [FOMO](https://en.wikipedia.org/wiki/Fear_of_missing_out) — you can conquer it!

Made using FastAPI.

## Available workers

### Worker: parser loop
asyncio coroutine initiated as task on FastAPI startup. It waits 3m, parses all feeds (provided by `swamp-api`) that require update and repeats forever.

## Available routes

| **URL**        | **Description**                           |
| ---            | ---                                       |
| /parse/        | Parse one URL.                            |
| /parse/async/  | Parse one URL asynchronously.             |
| /runner/       | Run non-async runner.                     |
| /runner/async/ | Run async runner.                         |
| /tests/        | Test-compare async and non-async runners. |
