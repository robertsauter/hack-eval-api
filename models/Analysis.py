from models.HackathonInformation import HackathonInformation
from pydantic import BaseModel
from typing import Literal


class StatisticalValues(BaseModel):
    participants: int
    average: float | None = None
    deviation: float | None = None
    distribution: dict[str, int]
    cronbach_alpha: float | None = None


class AnalysisSubQuestion(BaseModel):
    title: str
    statistical_values: StatisticalValues | None = None


class AnalysisMeasure(BaseModel):
    title: str
    question_type: Literal['single_question',
                           'group_question', 'score_question', 'category_question']
    answer_type: Literal['string_to_int', 'int', 'string']
    sub_questions: list[str | AnalysisSubQuestion] | None = None
    statistical_values: StatisticalValues | None = None
    answers: dict[str, int] | list[str] | None = None


class Analysis(HackathonInformation):
    results: list[AnalysisMeasure] = []
