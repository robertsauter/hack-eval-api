from pydantic import BaseModel
from models.HackathonInformation import Incentives, Venue, Type, Size

class Filter(BaseModel):
    incentives: list[Incentives] | None = None
    venue: list[Venue] | None = None
    size: list[Size] | None = None
    types: list[Type] | None = None