from datetime import datetime
from pydantic import BaseModel


class Update(BaseModel):
    name: str
    href: str
    datetime: datetime
