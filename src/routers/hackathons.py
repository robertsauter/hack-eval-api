'''Routes for handling hackathon objects'''

from fastapi import APIRouter, UploadFile, Form, Depends
from src.models.Filter import Filter
from src.models.RawHackathon import RawHackathon, RawAnswer
from src.models.HackathonInformation import HackathonInformationWithId
from src.models.Hackathon import Hackathon, SurveyMeasure, SubQuestion
from src.data.survey_questions import QUESTIONS, MISSING_VALUE_TITLE
from src.lib.http_exceptions import HTTP_415, HTTP_409
import pandas as pd
from pandas import DataFrame
from src.models.HackathonInformation import Venue, Incentives, Size
from typing import Annotated
from src.lib.database import hackathons_collection
from pymongo.collection import Collection
from jose import jwt
from src.lib.globals import SECRET_KEY, ALGORITHM, OAUTH2_SCHEME
from bson.objectid import ObjectId
from src.models.Survey import SurveyItem
import copy
from thefuzz import fuzz
import re
from datetime import datetime
import math

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
                return -1 if question.question_type == 'single_question' and value > 200 else value
            except:
                return -1
        case 'string':
            if question.question_type == 'category_question':
                if value in question.answers:
                    return value
                return MISSING_VALUE_TITLE
            return value
        case 'string_to_int':
            if value in question.answers:
                return question.answers[value]
            return -1


def set_value_google(question: SurveyMeasure, answers: dict[str, RawAnswer], item_id: str) -> None:
    '''Set the value for simple questions from Google Forms data'''
    if item_id in answers:
        value = answers[item_id].textAnswers.answers[0].value
    else:
        value = math.nan
    real_value = get_real_value(question, value)
    question.values.append(real_value)


def set_value_group_question_google(question: SurveyMeasure, answers: dict[str, RawAnswer], sub_items: dict) -> None:
    '''Set the values for a group question from Google Forms data'''
    for sub_question in question.sub_questions:
        if sub_question.title in sub_items:
            item_id = sub_items[sub_question.title]
            if item_id in answers:
                value = answers[item_id].textAnswers.answers[0].value
            else:
                value = math.nan
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


def concatenate_list_of_dict(dict_of_lists: dict[str, list], key: str, values: list) -> None:
    '''Concatenate a list in a dict with another list'''
    if key in dict_of_lists:
        dict_of_lists[key] += values
    else:
        dict_of_lists[key] = values


def get_numerical_values(question: SurveyMeasure, values: list[str | int]) -> list[int]:
    '''Get the values of a question or subquestion in numerical form'''
    numerical_values = []
    for value in values:
        if question.answer_type == 'string':
            numerical_values.append(question.answers.index(value))
        else:
            numerical_values.append(value)
    return numerical_values


def fill_dict_with_hackathon_information(dict_of_lists: dict[str, list], hackathon: Hackathon, participants: int) -> None:
    '''Fill a dict with all hackathon information values for all participants'''
    concatenate_list_of_dict(dict_of_lists, 'id', [
                             hackathon.title for i in range(participants)])
    concatenate_list_of_dict(dict_of_lists, 'start', [
                             hackathon.start.strftime('%d.%m.%y') for i in range(participants)])
    concatenate_list_of_dict(dict_of_lists, 'end', [
                             hackathon.end.strftime('%d.%m.%y') for i in range(participants)])
    concatenate_list_of_dict(dict_of_lists, 'incentives', [
                             hackathon.incentives for i in range(participants)])
    concatenate_list_of_dict(dict_of_lists, 'venue', [
                             hackathon.venue for i in range(participants)])
    concatenate_list_of_dict(dict_of_lists, 'size', [
                             hackathon.size for i in range(participants)])
    concatenate_list_of_dict(dict_of_lists, 'types', [
                             ', '.join(hackathon.types) for i in range(participants)])


def check_hackathon_uniqueness(hackathon: Hackathon, hackathons_collection: Collection):
    found = hackathons_collection.find_one({
        'title': hackathon.title,
        'start': hackathon.start,
        'end': hackathon.end
    })
    if found != None:
        HTTP_409('Hackathon already exists')


@router.post('/csv')
def upload_hackathon_csv(
    title: Annotated[str, Form()],
    incentives: Annotated[Incentives, Form()],
    venue: Annotated[Venue, Form()],
    size: Annotated[Size, Form()],
    types: Annotated[str, Form()],
    start: Annotated[datetime, Form()],
    end: Annotated[datetime, Form()],
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
            start=start,
            end=end,
            results=copy.deepcopy(QUESTIONS),
            created_by=user_id
        )
        check_hackathon_uniqueness(hackathon, hackathons)
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
        start=raw_hackathon.start,
        end=raw_hackathon.end,
        link=raw_hackathon.link,
        results=copy.deepcopy(QUESTIONS),
        created_by=user_id
    )
    check_hackathon_uniqueness(hackathon, hackathons)
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
    for hackathon in hackathons.find({'created_by': user_id}, sort=[('_id', -1)]):
        found_hackathons.append(HackathonInformationWithId(
            id=str(hackathon['_id']),
            title=hackathon['title'],
            incentives=hackathon['incentives'],
            venue=hackathon['venue'],
            size=hackathon['size'],
            types=hackathon['types'],
            start=hackathon['start'],
            end=hackathon['end'],
            link=hackathon['link']
        ))
    return found_hackathons


@router.get('/aggregated/csv')
def get_aggregated_hackathon_from_user_id(
    hackathons: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(OAUTH2_SCHEME)]
) -> str:
    '''Return a csv string, that contains all data of the uploaded hackathons of the logged in user'''
    user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['sub']
    result: dict[str, list] = {}
    for raw_hackathon in hackathons.find({'created_by': user_id}):
        hackathon = Hackathon.model_validate(raw_hackathon)

        # Get number of participants, by getting the first question with a filled list of values
        participants = None
        for question in hackathon.results:
            if question.values != None and len(question.values) > 0:
                participants = len(question.values)
                break
        fill_dict_with_hackathon_information(result, hackathon, participants)

        if participants != None:
            for question in hackathon.results:
                # Handle questions with subquestions
                if question.question_type == 'group_question' or question.question_type == 'score_question':
                    for sub_question in question.sub_questions:
                        title = f'{question.title} [{sub_question.title}]'
                        if len(sub_question.values) == 0:
                            concatenate_list_of_dict(
                                result, title, [None for i in range(participants)])
                        else:
                            numerical_values = get_numerical_values(
                                question, sub_question.values)
                            concatenate_list_of_dict(
                                result, title, numerical_values)
                # Handle questions without subquestions
                else:
                    if len(question.values) == 0:
                        concatenate_list_of_dict(
                            result, question.title, [None for i in range(participants)])
                    else:
                        numerical_values = numerical_values = get_numerical_values(
                            question, question.values)
                        concatenate_list_of_dict(
                            result, question.title, numerical_values)

        # Raise an exception, if no answers were found in the hackathon
        # Note: The above check for participants ignores questions with subquestions, so this might not be accurate in the future
        # (but right now every hackathon should have values for at least one question without subquestions, so it should be accurate)
        else:
            raise Exception(
                f'Hackathon {hackathon.title} seems to have no answers!')
    values_df = pd.DataFrame(result)
    return values_df.to_csv(index=False)


@router.delete('/{hackathon_id}')
def delete_hackathon(
    hackathon_id: str,
    hackathons: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(OAUTH2_SCHEME)]
) -> str:
    '''Delete a hackathon with the given id'''
    hackathons.delete_one({'_id': ObjectId(hackathon_id)})
    return 'Success'


@router.get('/amount')
def get_amount_of_found_hackathons(
    selected_hackathon_id,
    raw_filter: str,
    hackathons_collection: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(OAUTH2_SCHEME)]
) -> int:
    '''Get the amount of hackathons, that can be found in the database with a given filter combination'''
    filter_combination = Filter.model_validate_json(raw_filter)
    user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['sub']
    db_filter = {
        '_id': {'$ne': ObjectId(selected_hackathon_id)}
    }
    if filter_combination.incentives != None and len(filter_combination.incentives) > 0:
        db_filter['incentives'] = {
            '$in': filter_combination.incentives
        }
    if filter_combination.venue != None and len(filter_combination.venue) > 0:
        db_filter['venue'] = {
            '$in': filter_combination.venue
        }
    if filter_combination.size != None and len(filter_combination.size) > 0:
        db_filter['size'] = {
            '$in': filter_combination.size
        }
    if filter_combination.types != None and len(filter_combination.types) > 0:
        db_filter['types'] = {
            '$elemMatch': {
                '$in': filter_combination.types
            }
        }
    if filter_combination.onlyOwn:
        db_filter['created_by'] = user_id

    return hackathons_collection.count_documents(db_filter)
