'''Routes for handling hackathon objects'''

from fastapi import APIRouter, UploadFile, Form, Depends
from models.RawHackathon import RawHackathon, RawAnswer
from models.HackathonInformation import HackathonInformationWithId
from models.Hackathon import Hackathon, SurveyMeasure, SubQuestion
from data.survey_questions import QUESTIONS, MISSING_VALUE_TITLE
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
from thefuzz import fuzz
import re

SIMILARITY = 85

router = APIRouter()


def match_question(question: SurveyMeasure | SubQuestion, match_string: str) -> bool:
    '''Match for keywords in a title of an uploaded survey. If keywords do not match, try with fuzzy string matching'''
    matching = False
    pattern = re.compile(question.keywords, re.IGNORECASE)
    matching = pattern.search(match_string) != None
    if not matching:
        matching = fuzz.ratio(question.title, match_string) > SIMILARITY
    return matching


def set_value_csv(question: SurveyMeasure, raw_results: DataFrame) -> None:
    '''Set the value for a simple question from a CSV file'''
    for title in raw_results.keys():
        contained = match_question(question, title)
        if contained:
            print(f'Identified single question: {title}')
            for value in raw_results[title]:
                real_value = get_real_value(question, value)
                question.values.append(real_value)
            return


def set_value_group_question_csv(question: SurveyMeasure, raw_results: DataFrame) -> None:
    '''Set the values for a group question from a CSV file'''
    for sub_question in question.sub_questions:
        for title in raw_results.keys():
            title_parts = title.split('[')
            if len(title_parts) > 1:
                question_contained = match_question(question, title_parts[0])
                sub_question_contained = match_question(
                    sub_question, title_parts[1])
                if question_contained and sub_question_contained:
                    print(f'Identified group question: {title}')
                    for value in raw_results[title]:
                        real_value = get_real_value(question, value)
                        sub_question.values.append(real_value)
                    break


def map_hackathon_results_csv(empty_hackathon: Hackathon, raw_results: DataFrame) -> None:
    '''Map a hackathon from a CSV file to a hackathon object'''
    for question in empty_hackathon.results:
        match question.question_type:
            case 'single_question' | 'category_question':
                set_value_csv(question, raw_results)
            case 'group_question' | 'score_question':
                set_value_group_question_csv(question, raw_results)


def get_real_value(question: SurveyMeasure, value: str | int) -> int | str:
    '''Check which type of answer is expected and map, if possible'''
    match question.answer_type:
        case 'int':
            try:
                value = int(value)
                return 0 if question.question_type == 'single_question' and value > 200 else value
            except:
                return 0
        case 'string':
            if question.question_type == 'category_question':
                if value in question.answers:
                    return value
                return MISSING_VALUE_TITLE
            return value
        case 'string_to_int':
            if value in question.answers:
                return question.answers[value]
            return 0


def set_value_google(question: SurveyMeasure, answers: dict[str, RawAnswer], item_id: str) -> None:
    '''Set the value for simple questions from Google Forms data'''
    if item_id in answers:
        value = answers[item_id].textAnswers.answers[0].value
        real_value = get_real_value(question, value)
        question.values.append(real_value)


def set_value_group_question_google(question: SurveyMeasure, answers: dict[str, RawAnswer], sub_items: dict) -> None:
    '''Set the values for a group question from Google Forms data'''
    for sub_question in question.sub_questions:
        if sub_question.title in sub_items:
            item_id = sub_items[sub_question.title]
            if item_id in answers:
                value = answers[item_id].textAnswers.answers[0].value
                real_value = get_real_value(question, value)
                sub_question.values.append(real_value)


def find_question_google(question: SurveyMeasure, items: list[SurveyItem]) -> dict | str | None:
    '''Get a question id or all subquestion ids from Google Forms survey data'''
    for item in items:
        if item.title != None and match_question(question, item.title):
            match question.question_type:
                case 'single_question' | 'category_question':
                    return item.questionItem.question.questionId
                case 'group_question' | 'score_question':
                    if item.questionGroupItem != None:
                        group_question = {}
                        for sub_question in question.sub_questions:
                            for group_item in item.questionGroupItem.questions:
                                if group_item.rowQuestion.title != None and match_question(sub_question, group_item.rowQuestion.title):
                                    group_question[sub_question.title] = group_item.questionId
                                    break
                        return group_question
                    else:
                        return None


def map_hackathon_results_google(empty_hackathon: Hackathon, raw_hackathon: RawHackathon) -> None:
    '''Map a hackathon from Google forms to a hackathon object'''
    questions_in_hackathon = {}
    for question in empty_hackathon.results:
        found_question = find_question_google(
            question, raw_hackathon.survey.items)
        if found_question != None:
            questions_in_hackathon[question.title] = found_question
    for response in raw_hackathon.results.responses:
        for question in empty_hackathon.results:
            if question.title in questions_in_hackathon:
                match question.question_type:
                    case 'single_question' | 'category_question':
                        set_value_google(
                            question, response.answers, questions_in_hackathon[question.title])
                    case 'group_question' | 'score_question':
                        set_value_group_question_google(
                            question, response.answers, questions_in_hackathon[question.title])


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
) -> Hackathon | None:
    '''Save a hackathon in the database from a CSV file'''
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
        raw_results = pd.read_csv(file.file)
        map_hackathon_results_csv(hackathon, raw_results)
        hackathons.insert_one(hackathon.model_dump())
        return hackathon
    else:
        HTTP_415('Please provide a csv file.')


@router.post('/google')
def upload_hackathon_google(
    raw_hackathon: RawHackathon,
    hackathons: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(OAUTH2_SCHEME)]
) -> Hackathon:
    '''Save a hackathon from Google Forms in the database'''
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
    hackathons.delete_one({'_id': ObjectId(hackathon_id)})
    return 'Success'
