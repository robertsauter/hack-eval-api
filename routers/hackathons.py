'''Routes for handling hackathon objects'''

from fastapi import APIRouter, UploadFile, Form, Depends
from models.RawHackathon import RawHackathon, RawAnswer
from models.HackathonInformation import HackathonInformationWithId
from models.Hackathon import Hackathon, SurveyMeasure
import statistics
from data.survey_questions import QUESTIONS
from lib.http_exceptions import HTTP_415
import pandas as pd
from pandas import DataFrame
from models.HackathonInformation import Venue, Incentives, Size
from typing import Annotated
from lib.database import hackathons_collection
from pymongo.collection import Collection
from jose import jwt
from lib.globals import SECRET_KEY, ALGORITHM, OAUTH2_SCHEME
from bson.objectid import ObjectId
from models.Survey import SurveyItem
import copy

router = APIRouter()

def set_value_csv(question: SurveyMeasure, raw_results: DataFrame):
    if question.title in raw_results:
        for value in raw_results[question.title]:
            real_value = get_real_value(question, value)
            question.values.append(real_value)

def set_value_group_question_csv(question: SurveyMeasure, raw_results: DataFrame):
    for sub_question in question.sub_questions:
        title = f'{question.title} [{sub_question.title}]'
        if title in raw_results:
            for value in raw_results[title]:
                real_value = get_real_value(question, value)
                sub_question.values.append(real_value)

def set_value_score_question_csv(question: SurveyMeasure, raw_results: DataFrame):
    titles = []
    for sub_question in question.sub_questions:
        title = f'{question.title} [{sub_question}]'
        if title in raw_results:
            titles.append(title)
    if len(titles) > 0:
        values = []
        for i in range(raw_results.shape[0]):
            for title in titles:
                value = raw_results[title][i]
                real_value = get_real_value(question, value)
                values.append(real_value)
            question.values.append(round(statistics.fmean(values)))

def map_hackathon_results_csv(empty_hackathon: Hackathon, csv_file: UploadFile):
    raw_results = pd.read_csv(csv_file.file)
    for question in empty_hackathon.results:
        match question.question_type:
            case 'single_question' | 'category_question':
                set_value_csv(question, raw_results)
            case 'group_question':
                set_value_group_question_csv(question, raw_results)
            case 'score_question':
                set_value_score_question_csv(question, raw_results)

def get_real_value(question: SurveyMeasure, value: str | int):
    match question.answer_type:
        case 'int':
            try:
                return int(value)
            except:
                return 0
        case 'string':
            if question.question_type == 'category_question':
                if value in question.answers:
                    return value
                return question.answers[0]
            return value
        case 'string_to_int':
            if value in question.answers:
                return question.answers[value]
            return 0

def set_value_google(question: SurveyMeasure, answers: dict[str, RawAnswer], item_id: str):
    if item_id in answers:
        value = answers[item_id].textAnswers.answers[0].value
        real_value = get_real_value(question, value)
        question.values.append(real_value)

def set_value_score_question_google(question: SurveyMeasure, answers: dict[str, RawAnswer], sub_items: dict):
    all_values = []
    for sub_question in question.sub_questions:
        if sub_question in sub_items:
            item_id = sub_items[sub_question]
            if item_id in answers:
                value = answers[item_id].textAnswers.answers[0].value
                real_value = get_real_value(question, value)
                all_values.append(real_value)
    if len(all_values) > 0:
        question.values.append(round(statistics.fmean(all_values)))

def set_value_group_question_google(question: SurveyMeasure, answers: dict[str, RawAnswer], sub_items: dict):
    for sub_question in question.sub_questions:
        if sub_question.title in sub_items:
            item_id = sub_items[sub_question.title]
            if item_id in answers:
                value = answers[item_id].textAnswers.answers[0].value
                real_value = get_real_value(question, value)
                sub_question.values.append(real_value)

def find_question_google(question: SurveyMeasure, items: list[SurveyItem]):
    for item in items:
        if item.title != None and item.title == question.title:
            match question.question_type:
                case 'single_question' | 'category_question':
                    return item.questionItem.question.questionId
                case 'group_question' | 'score_question':
                    if item.questionGroupItem != None:
                        group_question = {}
                        for sub_question in question.sub_questions:
                            title = sub_question if question.question_type == 'score_question' else sub_question.title
                            for group_item in item.questionGroupItem.questions:
                                if group_item.rowQuestion.title != None and title == group_item.rowQuestion.title:
                                    group_question[title] = group_item.questionId
                                    break
                        return group_question
                    else:
                        return None

def map_hackathon_results_google(empty_hackathon: Hackathon, raw_hackathon: RawHackathon):
    questions_in_hackathon = {}
    for question in empty_hackathon.results:
        found_question = find_question_google(question, raw_hackathon.survey.items)
        if found_question != None:
            questions_in_hackathon[question.title] = found_question
    for response in raw_hackathon.results.responses:
        for question in empty_hackathon.results:
            if question.title in questions_in_hackathon:
                match question.question_type:
                    case 'single_question' | 'category_question':
                        set_value_google(question, response.answers, questions_in_hackathon[question.title])
                    case 'score_question':
                        set_value_score_question_google(question, response.answers, questions_in_hackathon[question.title])
                    case 'group_question':
                        set_value_group_question_google(question, response.answers, questions_in_hackathon[question.title])

@router.post('/csv')
def upload_hackathon_csv(
    title: Annotated[str, Form()],
    incentives: Annotated[Incentives, Form()],
    venue: Annotated[Venue, Form()],
    size: Annotated[Size, Form()],
    types: Annotated[str, Form()],
    file: UploadFile,
    hackathons: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    link: Annotated[str | None, Form()] = None,
):
    if file.content_type == 'text/csv' and file.filename.endswith('.csv'):
        user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['sub']
        type_list = types.split(',')
        hackathon = Hackathon(
            title=title,
            incentives=incentives,
            venue=venue,
            size=size,
            types=type_list,
            link=link,
            results=copy.deepcopy(QUESTIONS),
            created_by=user_id
        )
        map_hackathon_results_csv(hackathon, file)
        hackathons.insert_one(hackathon.model_dump())
        return hackathon
    else:
        HTTP_415('Please provide a csv file.')

@router.post('/google')
def upload_hackathon_google(
    raw_hackathon: RawHackathon,
    hackathons: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(OAUTH2_SCHEME)]
):
    user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['sub']
    hackathon = Hackathon(
        title=raw_hackathon.title,
        incentives=raw_hackathon.incentives,
        venue=raw_hackathon.venue,
        size=raw_hackathon.size,
        types=raw_hackathon.types,
        link=raw_hackathon.link,
        results=copy.deepcopy(QUESTIONS),
        created_by=user_id
    )
    map_hackathon_results_google(hackathon, raw_hackathon)
    hackathons.insert_one(hackathon.model_dump())
    return hackathon

@router.get('')
def get_hackathons_by_user_id(
    hackathons: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(OAUTH2_SCHEME)]
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
            size=hackathon['size'],
            types=hackathon['types'],
            link=hackathon['link']
        ))
    return found_hackathons

@router.delete('/{hackathon_id}')
def delete_hackathon(
    hackathon_id: str,
    hackathons: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(OAUTH2_SCHEME)]
    ) -> str:
    '''Delete a hackathon with the given id'''
    hackathons.delete_one({'_id': ObjectId(hackathon_id)});
    return 'Success'
