from pydantic import BaseModel


class ExplainedFeed(BaseModel):
    title: str
    href: str
    href_user: str
    private: bool
    frequency: str
    notes: str
    json: dict
