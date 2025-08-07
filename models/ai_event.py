from pydantic import BaseModel
from datetime import datetime


class AIEvent(BaseModel):
    name: str
    startDate: datetime
    endDate: datetime
    place: str
