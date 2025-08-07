from pydantic import BaseModel
from typing import List

from models.ai_event import AIEvent


class EventList(BaseModel):
    events: List[AIEvent]
