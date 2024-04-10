from pydantic import BaseModel


class RowQuestion(BaseModel):
    title: str


class SurveyQuestion(BaseModel):
    questionId: str
    textQuestion: dict | None = None
    rowQuestion: RowQuestion | None = None


class SurveyQuestionGroupItem(BaseModel):
    questions: list[SurveyQuestion]


class SurveyQuestionItem(BaseModel):
    question: SurveyQuestion


class SurveyItem(BaseModel):
    itemId: str
    title: str | None = None
    description: str | None = None
    questionItem: SurveyQuestionItem | None = None
    questionGroupItem: SurveyQuestionGroupItem | None = None


class SurveyInfo(BaseModel):
    title: str
    description: str
    documentTitle: str


class Survey(BaseModel):
    formId: str
    info: SurveyInfo
    revisionId: str
    responderUri: str
    items: list[SurveyItem]
