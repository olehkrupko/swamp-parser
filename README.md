# Swamp Parser

This is parsing back-end part of Swamp project which makes actual work of parsing feeds for updates. If you can't destroy [FOMO](https://en.wikipedia.org/wiki/Fear_of_missing_out) — you can conquer it!

Made using FastAPI.

## Workers

### Worker: parser loop
asyncio coroutine initiated as task on FastAPI startup. It waits 3m, parses all feeds (provided by [swamp-api](https://github.com/olehkrupko/swamp-api)) that require update and repeats forever.

## Routes

| **URL**           |**Description**                           |
| ---               | ---                                      |
| /ingest/          | Ingest all feeds that requires an update.|
| /ingest/{feed_id} | Ingest one feed by URL.                  |
| /parse/updates    | Parse updates from one feed by URL.      |
| /parse/explained  | Parse details about one feed.            |
