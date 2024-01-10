'''Routes for handling hackathon objects'''

from fastapi import APIRouter, UploadFile
from models.RawHackathon import RawHackathon, RawAnswer
from fastapi.security import OAuth2PasswordBearer
from models.Hackathon import Hackathon, Measures
import statistics
from data.survey_questions import ANSWERS_MAP, QUESTION_TITLES_MAP, SPECIAL_QUESTION_TITLES_SET
from lib.helpers import getattr_with_initial_value
from lib.http_exceptions import HTTP_415
import pandas as pd

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/login')

router = APIRouter()

def get_raw_answer_google(answers: dict[str, RawAnswer], item_id: str) -> RawAnswer | None:
    return answers[item_id] if item_id in answers else None

def set_special_question(results: Measures, parent_title: str, child_title: str, value: str):
    parent_attribute = getattr(results, parent_title)
    child_attribute = getattr_with_initial_value(parent_attribute, child_title, [])
    child_attribute.append(ANSWERS_MAP[parent_title][value])

def map_hackathon_results_google(raw_hackathon: RawHackathon) -> Measures:
    '''Map a raw hackathon from google forms to a hackathon, that can be saved in the database'''
    results = Measures()
    for response in raw_hackathon.results.responses:
        for item in raw_hackathon.survey.items:
            #Single item questions
            if item.questionItem != None and item.title in QUESTION_TITLES_MAP and item.title not in SPECIAL_QUESTION_TITLES_SET:
                answer = get_raw_answer_google(response.answers, item.questionItem.question.questionId)
                if answer != None:
                    title = QUESTION_TITLES_MAP[item.title]
                    value = answer.textAnswers.answers[0].value
                    final_value = int(value) if item.questionItem.question.textQuestion != None else ANSWERS_MAP[title][value]
                    getattr_with_initial_value(results, title, []).append(final_value)
            #Question groups with subquestions
            elif item.questionGroupItem != None and item.title in SPECIAL_QUESTION_TITLES_SET:
                parent_title = QUESTION_TITLES_MAP[item.title]
                for question in item.questionGroupItem.questions:
                    answer = get_raw_answer_google(response.answers, question.questionId)
                    if answer != None and question.rowQuestion.title in QUESTION_TITLES_MAP:
                        child_title = QUESTION_TITLES_MAP[question.rowQuestion.title]
                        value = answer.textAnswers.answers[0].value
                        set_special_question(results, parent_title, child_title, value)
            #Question groups that form a single score
            elif item.questionGroupItem != None and item.title in QUESTION_TITLES_MAP:
                answer_values = []
                title = QUESTION_TITLES_MAP[item.title]
                for question in item.questionGroupItem.questions:
                    answer = get_raw_answer_google(response.answers, question.questionId)
                    if answer != None:
                        value = answer.textAnswers.answers[0].value
                        answer_values.append(ANSWERS_MAP[title][value])
                if len(answer_values) > 0:
                    getattr_with_initial_value(results, title, []).append(round(statistics.fmean(answer_values)))
    return results

def map_hackathon_results_csv(csv_file: UploadFile) -> Hackathon:
    hackathon = Hackathon(
        title='',
        venue='in-person',
        participants=10,
        type='prototype',
        results=Measures()
    )
    results = pd.read_csv(csv_file.file)
    question_group_title = ''
    question_group_values = []
    question_group_index = 0
    for raw_title_hashable in results:
        raw_title = str(raw_title_hashable)
        #Handle group questions with single score
        if question_group_title != '' and question_group_title not in raw_title:
            for value_group in question_group_values:
                getattr_with_initial_value(hackathon.results, QUESTION_TITLES_MAP[question_group_title], []).append(round(statistics.fmean(value_group)))
            question_group_title = ''
            question_group_values = []
        sections = raw_title.split(' [', 1)
        #Handle group questions
        if len(sections) > 1:
            raw_parent_title = sections[0]
            parent_title = QUESTION_TITLES_MAP[raw_parent_title] if raw_parent_title in QUESTION_TITLES_MAP else None
            if parent_title != None:
                #Handle group questions with subquestions
                if raw_parent_title in SPECIAL_QUESTION_TITLES_SET:
                    raw_child_title = sections[1].strip(']')
                    child_title = QUESTION_TITLES_MAP[raw_child_title] if raw_child_title in QUESTION_TITLES_MAP else None
                    if child_title != None:
                        for value in results.get(raw_title_hashable):
                            set_special_question(hackathon.results, parent_title, child_title, value)
                #Prepare group question with single score
                else:
                    values = results.get(raw_title_hashable)
                    for value in values:
                        if len(question_group_values) < values.size:
                            question_group_values.append([])
                        final_value = ANSWERS_MAP[parent_title][value] if type(value) is str else ANSWERS_MAP[parent_title][str(value)] if type(value) is int else 0
                        question_group_values[question_group_index].append(final_value)
                        question_group_index += 1
                    question_group_title = raw_parent_title
                    question_group_index = 0
        #Handle single questions
        else:
            if raw_title in QUESTION_TITLES_MAP:
                title = QUESTION_TITLES_MAP[raw_title]
                attribute = getattr_with_initial_value(hackathon.results, title, [])
                for value in results.get(raw_title_hashable):
                    final_value = ANSWERS_MAP[title][value] if title in ANSWERS_MAP else int(value)
                    attribute.append(final_value)
    return hackathon

@router.post('/google')
def upload_hackathon_google(raw_hackathon: RawHackathon) -> Hackathon:
    '''Process and save a hackathon object from google forms in the database'''
    hackathon = Hackathon(
        title=raw_hackathon.title,
        venue=raw_hackathon.venue,
        participants=raw_hackathon.participants,
        type=raw_hackathon.type,
        results=map_hackathon_results_google(raw_hackathon)
    )
    return hackathon

@router.post('/csv')
def upload_hackathon_csv(csv_file: UploadFile) -> Hackathon:
    '''Process and save a hackathon object from a csv file in the database'''
    if csv_file.content_type == 'text/csv' and csv_file.filename.endswith('.csv'):
        return map_hackathon_results_csv(csv_file)
    else:
        HTTP_415('Please provide a csv file.')