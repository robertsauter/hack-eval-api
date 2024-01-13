'''Routes for handling hackathon objects'''

from fastapi import APIRouter, UploadFile, Form, Depends
from models.RawHackathon import RawHackathon, RawAnswer
from fastapi.security import OAuth2PasswordBearer
from models.Hackathon import Hackathon, Measures
from models.HackathonInformation import HackathonInformationWithId
import statistics
from data.survey_questions import ANSWERS_MAP, QUESTION_TITLES_MAP, SPECIAL_QUESTION_TITLES_SET
from lib.helpers import getattr_with_initial_value
from lib.http_exceptions import HTTP_415
import pandas as pd
from typing import Annotated
from models.HackathonInformation import Venue, Type, Incentives
from typing import Annotated
from lib.database import hackathons_collection
from pymongo.collection import Collection
import math
from jose import jwt
from lib.globals import SECRET_KEY, ALGORITHM
from bson.objectid import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/login')

router = APIRouter()

def get_raw_answer_google(answers: dict[str, RawAnswer], item_id: str) -> RawAnswer | None:
    return answers[item_id] if item_id in answers else None

def set_special_question(results: Measures, parent_title: str, child_title: str, value: str):
    '''Set a question group with subquestions in a Measures object'''
    parent_attribute = getattr(results, parent_title)
    child_attribute = getattr_with_initial_value(parent_attribute, child_title, [])
    final_value = get_real_value(parent_title, value)
    child_attribute.append(final_value)

def get_real_value(title: str, value: any):
    '''Determine which type a value has (missing values return 0)'''
    if type(value) is str:
        if title in ANSWERS_MAP and value in ANSWERS_MAP[title]:
            return ANSWERS_MAP[title][value]
        return 0
    elif type(value) is float:
        if math.isnan(value):
            return 0
        return round(value)
    elif type(value) is int:
        return value
    return 0

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

def map_hackathon_results_csv(csv_file: UploadFile) -> Measures:
    '''Map a raw hackathon from a csv file to a hackathon, that can be saved in the database'''
    results = Measures()
    raw_results = pd.read_csv(csv_file.file)
    question_group_title = ''
    question_group_values = []
    question_group_index = 0
    for raw_title_hashable in raw_results:
        raw_title = str(raw_title_hashable)
        #Handle group questions with single score
        if question_group_title != '' and question_group_title not in raw_title:
            for value_group in question_group_values:
                getattr_with_initial_value(results, QUESTION_TITLES_MAP[question_group_title], []).append(round(statistics.fmean(value_group)))
            question_group_title = ''
            question_group_values = []
        sections = raw_title.split(' [', 1)
        #Group questions
        if len(sections) > 1:
            raw_parent_title = sections[0]
            parent_title = QUESTION_TITLES_MAP[raw_parent_title] if raw_parent_title in QUESTION_TITLES_MAP else None
            if parent_title != None:
                #Handle group questions with subquestions
                if raw_parent_title in SPECIAL_QUESTION_TITLES_SET:
                    raw_child_title = sections[1].strip(']')
                    child_title = QUESTION_TITLES_MAP[raw_child_title] if raw_child_title in QUESTION_TITLES_MAP else None
                    if child_title != None:
                        for value in raw_results.get(raw_title_hashable):
                            set_special_question(results, parent_title, child_title, value)
                #Prepare group question with single score
                else:
                    values = raw_results.get(raw_title_hashable)
                    for value in values:
                        if len(question_group_values) < values.size:
                            question_group_values.append([])
                        question_group_values[question_group_index].append(get_real_value(parent_title, value))
                        question_group_index += 1
                    question_group_title = raw_parent_title
                    question_group_index = 0
        #Handle single questions
        else:
            if raw_title in QUESTION_TITLES_MAP:
                title = QUESTION_TITLES_MAP[raw_title]
                attribute = getattr_with_initial_value(results, title, [])
                for value in raw_results.get(raw_title_hashable):
                    attribute.append(get_real_value(title, value))
    return results

@router.post('/google')
def upload_hackathon_google(
    raw_hackathon: RawHackathon,
    hackathons: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(oauth2_scheme)]
    ) -> Hackathon:
    '''Process and save a hackathon object from google forms in the database'''
    user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['sub']
    hackathon = Hackathon(
        title=raw_hackathon.title,
        incentives=raw_hackathon.incentives,
        venue=raw_hackathon.venue,
        participants=raw_hackathon.participants,
        type=raw_hackathon.type,
        results=map_hackathon_results_google(raw_hackathon),
        created_by=user_id
    )
    hackathons.insert_one(hackathon.model_dump())
    return hackathon

@router.post('/csv')
def upload_hackathon_csv(
    title: Annotated[str, Form()],
    incentives: Annotated[Incentives, Form()],
    venue: Annotated[Venue, Form()],
    participants: Annotated[int, Form()],
    type: Annotated[Type, Form()],
    file: UploadFile,
    hackathons: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(oauth2_scheme)]
    ) -> Hackathon:
    '''Process and save a hackathon object from a csv file in the database'''
    if file.content_type == 'text/csv' and file.filename.endswith('.csv'):
        user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['sub']
        hackathon = Hackathon(
            title=title,
            incentives=incentives,
            venue=venue,
            participants=participants,
            type=type,
            results=map_hackathon_results_csv(file),
            created_by=user_id
        )
        hackathons.insert_one(hackathon.model_dump())
        return hackathon
    else:
        HTTP_415('Please provide a csv file.')

@router.get('')
def get_hackathons_by_user_id(
    hackathons: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(oauth2_scheme)]
    ) -> list[HackathonInformationWithId]:
    '''Find all hackathons of the logged in user'''
    user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['sub']
    found_hackathons = []
    for hackathon in hackathons.find({'created_by': user_id}):
        found_hackathons.append(HackathonInformationWithId(
            id=str(hackathon['_id']),
            title=hackathon['title'],
            incentives=hackathon['incentives'],
            venue=hackathon['venue'],
            participants=hackathon['participants'],
            type=hackathon['type']
        ))
    return found_hackathons

@router.delete('/{hackathon_id}')
def delete_hackathon(
    hackathon_id: str,
    hackathons: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(oauth2_scheme)]
    ) -> str:
    '''Delete a hackathon with the given id'''
    hackathons.delete_one({'_id': ObjectId(hackathon_id)});
    return 'Success'
