from src.models.HackathonInformation import HackathonInformation
from pydantic import BaseModel
from typing import Literal


class SubQuestion(BaseModel):
    title: str
    values: list[int | str]
    keywords: str | None = None
    reverse: bool = False


class SurveyMeasure(BaseModel):
    title: str
    display_name: str
    question_type: Literal['single_question',
                           'group_question', 'score_question', 'category_question']
    answer_type: Literal['string_to_int', 'int', 'string']
    values: list[int | str] | None = None
    sub_questions: list[SubQuestion] | None = None
    answers: dict[str, int] | list[str] | None = None
    keywords: str | None = None


class Hackathon(HackathonInformation):
    results: list[SurveyMeasure] = []
    created_by: str
