from pydantic import BaseModel
from typing import Literal

Incentives = Literal['competition', 'collaboration']

Venue = Literal['in-person', 'virtual', 'hybrid']

Type = Literal['prototype', 'conceptual', 'analysis', 'education', 'community', 'ideation']

class HackathonInformation(BaseModel):
    title: str
    incentives: Incentives
    venue: Venue
    participants: int
    types: list[Type]

class HackathonInformationWithId(HackathonInformation):
    id: str