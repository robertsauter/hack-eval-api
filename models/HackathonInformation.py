from pydantic import BaseModel
from typing import Literal

Venue = Literal['in-person', 'virtual', 'hybrid']

Type = Literal['prototype', 'conceptual', 'analysis', 'education', 'community', 'ideation']

class HackathonInformation(BaseModel):
    title: str
    venue: Venue
    participants: int
    type: Type