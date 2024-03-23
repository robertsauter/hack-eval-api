from pydantic import BaseModel
from typing import Literal
from datetime import datetime

Incentives = Literal['competitive', 'cooperative']

Venue = Literal['in person', 'online', 'hybrid']

Type = Literal['prototype', 'conceptual',
               'analysis', 'education', 'community', 'ideation']

Size = Literal['small', 'medium', 'large']


class HackathonInformation(BaseModel):
    title: str
    incentives: Incentives
    venue: Venue
    size: Size
    types: list[Type]
    start: datetime
    end: datetime
    link: str | None = None


class HackathonInformationWithId(HackathonInformation):
    id: str
