# Swamp Parser

This is parsing back-end part of Swamp project which makes actual work of parsing feeds for updates. If you can't destroy [FOMO](https://en.wikipedia.org/wiki/Fear_of_missing_out) — you can conquer it!

Made using FastAPI.

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available workers

### Worker: parser loop
Parse all feeds that require update using asyncio.

## Available routes

### /parse/
Parse one URL.

### /parse/async/
Parse one URL asynchronously.

### /runner/
Run non-async runner.

### /runner/async/
Run async runner.

### /tests/
Test-compare async and non-async runners.
