from pydantic import BaseModel
from enum import Enum

class Venue(Enum):
    IN_PERSON = 'in-person'
    VIRTUAL = 'virtual',
    HYBRID = 'hybrid'

class Type(Enum):
    PROTOTYPE = 'prototype'
    CONCEPTUAL = 'conceptual'
    ANALYSIS = 'analysis'
    EDUCATION = 'education'
    COMMUNITY = 'community'
    IDEATION = 'ideation'

class HackathonInformation(BaseModel):
    title: str
    venue: Venue
    participants: int
    type: Type