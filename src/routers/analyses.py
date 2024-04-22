'''Routes for filtering hackathons and creating analysis data'''

from fastapi import APIRouter, Depends
import json
from typing import Annotated
from pymongo.collection import Collection
from src.lib.database import hackathons_collection
from bson.objectid import ObjectId
from typing import Annotated
from src.lib.globals import OAUTH2_SCHEME, ALGORITHM, SECRET_KEY
from src.models.Filter import Filter
from src.lib.http_exceptions import HTTP_422
from src.models.Hackathon import Hackathon, SurveyMeasure, SubQuestion
from src.models.Analysis import Analysis, StatisticalValues, AnalysisMeasure, AnalysisSubQuestion
import pandas as pd
import pingouin as pg
import math
from datetime import datetime
from jose import jwt
import time
import numpy as np

router = APIRouter()


def build_filtered_hackathon(filter_combination: dict, hackathons_collection: Collection, user_id: str) -> Hackathon | None:
    '''Create a single dataset, that combines the hackathons, that were found from the filter combination'''
    filter_values = {}
    try:
        Filter.model_validate(filter_combination)
    except:
        HTTP_422('Filter combination is invalid')
    for key in filter_combination:
        if key != 'name' and len(filter_combination[key]) != 0:
            if key == 'types':
                filter_values[key] = {'$elemMatch': {
                    "$in": filter_combination[key]}}
            elif key == 'onlyOwn':
                filter_values['created_by'] = user_id
            else:
                filter_values[key] = {'$in': filter_combination[key]}
    cursor = hackathons_collection.find(filter_values)
    final_hackathon = None
    for hackathon_dict in cursor:
        hackathon = Hackathon.model_validate(hackathon_dict)
        if final_hackathon == None:
            final_hackathon = hackathon
        else:
            combine_hackathon_values(
                final_hackathon.results, hackathon.results)
    if final_hackathon != None:
        name = filter_combination['name'] if 'name' in filter_combination else 'All hackathons'
        final_hackathon.title = name
    return final_hackathon


def check_if_subquestions_are_even(sub_questions: list[SubQuestion]) -> bool:
    '''Check if all subquestions have the same amount of values'''
    lengths = [len(sub_question.values) for sub_question in sub_questions]
    return len(set(lengths)) == 1


def combine_hackathon_values(first_hackathon: list[SurveyMeasure], second_hackathon: list[SurveyMeasure]) -> None:
    '''Add values of the second to the first hackathon'''
    for i in range(len(first_hackathon)):
        if first_hackathon[i].question_type == 'group_question':
            for j in range(len(first_hackathon[i].sub_questions)):
                first_hackathon[i].sub_questions[j].values.extend(
                    second_hackathon[i].sub_questions[j].values)
        elif first_hackathon[i].question_type == 'score_question':
            # Remove values from first hackathon, if subquestions of the first hackathon don't have the same amount of values
            is_first_hackathon_even = check_if_subquestions_are_even(
                first_hackathon[i].sub_questions)
            if not is_first_hackathon_even:
                for sub_question in first_hackathon[i].sub_questions:
                    sub_question.values = []
            # Don't append values, if subquestions of the second hackathon don't have the same amount of values
            is_second_hackathon_even = check_if_subquestions_are_even(
                second_hackathon[i].sub_questions)
            if is_second_hackathon_even:
                for j in range(len(first_hackathon[i].sub_questions)):
                    first_hackathon[i].sub_questions[j].values.extend(
                        second_hackathon[i].sub_questions[j].values)
            else:
                pass
        else:
            first_hackathon[i].values.extend(second_hackathon[i].values)


def get_and_prepare_hackathon(hackathon_id: str, hackathons_collection: Collection) -> Hackathon:
    '''Get a hackathon from the database and remove score questions where the subquestions don't have the same amount of values'''
    hackathon_dict = hackathons_collection.find_one(
        {'_id': ObjectId(hackathon_id)})
    hackathon = Hackathon.model_validate(hackathon_dict)
    for question in hackathon.results:
        if question.question_type == 'score_question':
            even = check_if_subquestions_are_even(question.sub_questions)
            if not even:
                for sub_question in question.sub_questions:
                    sub_question.values = []
    return hackathon


def create_statistics(values: np.ndarray, question_type: str) -> StatisticalValues:
    '''Create statistical values for a list of values'''
    unique, counts = np.unique(values, return_counts=True)
    if question_type == 'category_question':
        distribution = dict(zip(unique, counts))
        return StatisticalValues(participants=values.size, distribution=distribution)
    else:
        unique_strings = np.char.mod('%d', unique)
        distribution = dict(zip(unique_strings, counts))
    deviation = np.std(values) if values.size > 1 else 0
    average = np.mean(values) if values.size > 1 else 0
    return StatisticalValues(
        participants=values.size,
        distribution=distribution,
        deviation=deviation,
        average=average
    )


def create_statistics_score_question(values: np.ndarray, question_type: str) -> StatisticalValues:
    '''Create statistical values for a score question'''
    sub_question_dataframe = pd.DataFrame(values)
    cronbach_alpha = None
    if values.shape[0] > 0 and values.shape[1] > 0:
        cronbach_alpha = pg.cronbach_alpha(sub_question_dataframe)
    final_values = np.mean(values, axis=0)
    statistical_values = create_statistics(
        final_values, question_type)
    if cronbach_alpha != None:
        statistical_values.cronbach_alpha = 0 if math.isnan(
            cronbach_alpha[0]) else cronbach_alpha[0]
    return statistical_values


def create_analysis(hackathon: Hackathon) -> Analysis:
    '''Create an object, that contains statistical values for every measure of a survey'''
    analysis = Analysis(
        title=hackathon.title,
        incentives=hackathon.incentives,
        venue=hackathon.venue,
        size=hackathon.size,
        types=hackathon.types,
        start=hackathon.start,
        end=hackathon.end,
        link=hackathon.link
    )
    for question in hackathon.results:
        measure = AnalysisMeasure(
            title=question.title,
            question_type=question.question_type,
            answer_type=question.answer_type,
            answers=question.answers
        )
        if question.question_type == 'group_question':
            measure.sub_questions = []
            for sub_question in question.sub_questions:
                measure_sub_question = AnalysisSubQuestion(
                    title=sub_question.title)
                measure_sub_question.statistical_values = create_statistics(
                    np.array(sub_question.values), question.question_type)
                measure.sub_questions.append(measure_sub_question)
        elif question.question_type == 'score_question':
            values = []
            measure.sub_questions = []
            for sub_question in question.sub_questions:
                measure_sub_question = AnalysisSubQuestion(
                    title=sub_question.title)
                measure_sub_question.statistical_values = create_statistics(
                    np.array(sub_question.values), question.question_type)
                measure.sub_questions.append(measure_sub_question)

                sub_values = sub_question.values
                if sub_question.reverse:
                    max_value = len(question.answers.values())
                    sub_values = list(map(lambda value: abs(
                        value - (max_value + 1)), sub_values))
                values.append(sub_values)
            try:
                measure.statistical_values = create_statistics_score_question(
                    np.array(values), question.question_type)
            except:
                pass
        else:
            measure.statistical_values = create_statistics(
                np.array(question.values), question.question_type)
        analysis.results.append(measure)
    return analysis


@router.get('')
def get_analyses(
    hackathons_collection: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    hackathon_id: str = '',
    filters: str = '[]'
) -> list[Analysis]:
    '''Create all analyses given a list of filters'''
    user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['sub']
    hackathon = get_and_prepare_hackathon(hackathon_id, hackathons_collection)
    analyses = [create_analysis(hackathon)]
    decoded_filters = json.loads(filters)
    if len(decoded_filters) == 0:
        decoded_filters.append({})
    for filter_combination in decoded_filters:
        filtered_hackathon = build_filtered_hackathon(
            filter_combination, hackathons_collection, user_id)
        if filtered_hackathon != None:
            analyses.append(create_analysis(filtered_hackathon))
        else:
            # Append analysis with empty results
            analyses.append(Analysis(
                title=filter_combination['name'],
                incentives='cooperative',
                venue='hybrid',
                size='small',
                types=['analysis'],
                start=datetime.now(),
                end=datetime.now()
            ))
    return analyses
