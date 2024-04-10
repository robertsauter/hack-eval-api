from pydantic import BaseModel
from src.models.HackathonInformation import Incentives, Venue, Type, Size


class Filter(BaseModel):
    name: str = ''
    incentives: list[Incentives] | None = None
    venue: list[Venue] | None = None
    size: list[Size] | None = None
    types: list[Type] | None = None
    onlyOwn: bool = False


class FilterWithId(Filter):
    id: str
