from pydantic import BaseModel
from enum import Enum

Venue = Enum('Venue', ['in-person', 'virtual', 'hybrid'])
Type = Enum('Type', ['prototype', 'conceptual', 'analysis', 'education', 'community', 'ideation'])

class Answer(BaseModel):
    value: str

class TextAnswer(BaseModel):
    answers: list[Answer]

class RawAnswer(BaseModel):
    questionId: str
    textAnswers:TextAnswer

class RawResponse(BaseModel):
    responseId: str
    createTime: str
    lastSubmittedTime: str
    answers: dict[str, RawAnswer]

class RawResults(BaseModel):
    responses: list[RawResponse]

class RawHackathon(BaseModel):
    title: str
    venue: str
    participants: int
    type: str
    results: RawResults