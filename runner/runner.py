import os
import time

import requests

import parsers.base as parser_base


def runner():
    feeds = requests.get(os.environ["SWAMP_API_FEEDS"]).json()

    results = []
    for feed in feeds:
        updates = parser_base.parse_href(feed["href"])
        requests.put(
            f"{ os.environ['SWAMP_API_FEEDS'] }/feeds/{ feed['feed_id'] }/push/",
            data=updates,
        )
        results.append(
            {
                'len': type(res),
            }
        )

    return results
