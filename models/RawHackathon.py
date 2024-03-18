from pydantic import BaseModel
from models.HackathonInformation import HackathonInformation
from models.Survey import Survey


class Answer(BaseModel):
    value: str


class TextAnswer(BaseModel):
    answers: list[Answer]


class RawAnswer(BaseModel):
    questionId: str
    textAnswers: TextAnswer


class RawResponse(BaseModel):
    responseId: str
    createTime: str
    lastSubmittedTime: str
    answers: dict[str, RawAnswer]


class RawResults(BaseModel):
    responses: list[RawResponse]


class RawHackathon(HackathonInformation):
    survey: Survey
    results: RawResults
