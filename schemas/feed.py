from pydantic import BaseModel
from typing import Self


# feed with unnecessary fields cut off
class Feed(BaseModel):
    _id: int
    title: str  # not REALLY needed
    href: str

    def from_full(full_feed: dict) -> Self:
        return {
            "_id": full_feed["_id"],
            "href": full_feed["href"],
            "title": full_feed["title"],
        }
