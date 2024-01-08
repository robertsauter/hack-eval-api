'''Routes for handling hackathon objects'''

from fastapi import APIRouter
from models.RawHackathon import RawHackathon
from fastapi.security import OAuth2PasswordBearer
from models.Hackathon import Hackathon, Measures
import statistics
from data.survey_questions import ANSWERS_MAP, QUESTION_TITLES_MAP, SPECIAL_QUESTION_TITLES_SET

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/login')

router = APIRouter()

def map_hackathon_results(raw_hackathon: RawHackathon) -> Hackathon:
    '''Map a raw hackathon from google forms to a hackathon, that can be saved in the database'''
    hackathon = Hackathon(
        title=raw_hackathon.title,
        venue=raw_hackathon.venue,
        participants=raw_hackathon.participants,
        type=raw_hackathon.type,
        results=Measures()
    )
    for response in raw_hackathon.results.responses:
        for item in raw_hackathon.survey.items:
            #Single item questions
            if item.questionItem != None and item.title in QUESTION_TITLES_MAP:
                answer = response.answers[item.questionItem.question.questionId] if item.questionItem.question.questionId in response.answers else None
                if answer != None:
                    title = QUESTION_TITLES_MAP[item.title]
                    value = answer.textAnswers.answers[0].value
                    if not title in hackathon.results:
                        setattr(hackathon.results, title, [])
                    attribute = getattr(hackathon.results, title)
                    if item.questionItem.question.textQuestion != None:
                        attribute.append(int(value))
                    else:
                        attribute.append(ANSWERS_MAP[title][value])
            #Question groups with subquestions
            elif item.questionGroupItem != None and item.title in SPECIAL_QUESTION_TITLES_SET:
                parent_title = QUESTION_TITLES_MAP[item.title]
                for question in item.questionGroupItem.questions:
                    answer = response.answers[question.questionId] if question.questionId in response.answers else None
                    if answer != None and question.rowQuestion.title in QUESTION_TITLES_MAP:
                        child_title = QUESTION_TITLES_MAP[question.rowQuestion.title]
                        value = answer.textAnswers.answers[0].value
                        parent_attribute = getattr(hackathon.results, parent_title)
                        if not getattr(parent_attribute, child_title, False):
                            setattr(parent_attribute, child_title, [])
                        child_attribute = getattr(parent_attribute, child_title)
                        child_attribute.append(ANSWERS_MAP[parent_title][value])
            #Question groups that form a single score
            elif item.questionGroupItem != None and item.title in QUESTION_TITLES_MAP:
                answer_values = []
                title = QUESTION_TITLES_MAP[item.title]
                for question in item.questionGroupItem.questions:
                    answer = response.answers[question.questionId] if question.questionId in response.answers else None
                    if answer != None:
                        value = answer.textAnswers.answers[0].value
                        answer_values.append(ANSWERS_MAP[title][value])
                        if not title in hackathon.results:
                            setattr(hackathon.results, title, [])
                if len(answer_values) > 0:
                    if not title in hackathon.results:
                        setattr(hackathon.results, title, [])
                    getattr(hackathon.results, title).append(round(statistics.fmean(answer_values)))
    return hackathon

@router.post('')
def upload_hackathon(raw_hackathon: RawHackathon) -> Hackathon:
    '''Process and save a hackathon object in the database'''
    return map_hackathon_results(raw_hackathon)