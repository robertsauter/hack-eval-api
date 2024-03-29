'''Routes for filtering hackathons and creating analysis data'''

from fastapi import APIRouter, Depends
import json
from typing import Annotated
from pymongo.collection import Collection
from lib.database import hackathons_collection
from bson.objectid import ObjectId
from typing import Annotated
from lib.globals import OAUTH2_SCHEME, ALGORITHM, SECRET_KEY
from models.Filter import Filter
from lib.http_exceptions import HTTP_422
from models.Hackathon import Hackathon, SurveyMeasure
import statistics
from models.Analysis import Analysis, StatisticalValues, AnalysisMeasure, AnalysisSubQuestion
import pandas as pd
import pingouin as pg
import math
from datetime import datetime
from jose import jwt

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
                final_hackathon.results, hackathon.results, False)
    if final_hackathon != None:
        name = filter_combination['name'] if 'name' in filter_combination else 'All hackathons'
        final_hackathon.title = name
    return final_hackathon


def extend_values(first: list[int | str], second: list[int | str], strict: bool) -> None:
    '''Extend an array with a second one. If strict flag is set, remove all values if one of the arrays is empty'''
    if strict:
        if len(first) != 0 and len(second) != 0:
            first.extend(second)
        else:
            first.clear()
    else:
        first.extend(second)


def combine_hackathon_values(first_hackathon: list[SurveyMeasure], second_hackathon: list[SurveyMeasure], strict: bool) -> None:
    '''Add values of the second to the first hackathon. Remove all measures, that are not contained in both'''
    for i in range(len(first_hackathon)):
        if first_hackathon[i].question_type == 'group_question':
            for j in range(len(first_hackathon[i].sub_questions)):
                extend_values(first_hackathon[i].sub_questions[j].values,
                              second_hackathon[i].sub_questions[j].values, strict)
        elif first_hackathon[i].question_type == 'score_question':
            # Don't return score questions where subquestions don't have the same amount of values
            length = len(second_hackathon[i].sub_questions[0].values)
            is_uneven = False
            for j in range(len(second_hackathon[i].sub_questions)):
                if len(second_hackathon[i].sub_questions[j].values) != length:
                    is_uneven = True
            if not is_uneven:
                for j in range(len(first_hackathon[i].sub_questions)):
                    extend_values(first_hackathon[i].sub_questions[j].values,
                                  second_hackathon[i].sub_questions[j].values, strict)
        else:
            extend_values(first_hackathon[i].values,
                          second_hackathon[i].values, strict)


def build_single_hackathon(hackathon_ids: list[str], hackathons_collection: Collection) -> Hackathon | None:
    '''Turn a list of hackathons into a single dataset'''
    hackathon_object_ids = [ObjectId(id) for id in hackathon_ids]
    hackathons_cursor = hackathons_collection.find(
        {'_id': {'$in': hackathon_object_ids}})
    final_hackathon = None
    for hackathon_dict in hackathons_cursor:
        hackathon = Hackathon.model_validate(hackathon_dict)
        if final_hackathon == None:
            final_hackathon = hackathon
        else:
            combine_hackathon_values(
                final_hackathon.results, final_hackathon.results, True)
    return final_hackathon


def create_statistics(values: list[int | str], question_type: str) -> StatisticalValues:
    '''Create statistical values for a list of values'''
    participants = len(values)
    distribution = {}
    for value in values:
        value_as_string = str(value)
        if value_as_string in distribution:
            distribution[value_as_string] += 1
        else:
            distribution[value_as_string] = 1
    if question_type == 'category_question':
        return StatisticalValues(participants=participants, distribution=distribution)
    deviation = statistics.stdev(values) if len(values) > 1 else 0
    average = statistics.fmean(values) if len(values) > 0 else None
    return StatisticalValues(
        participants=participants,
        distribution=distribution,
        deviation=deviation,
        average=average
    )


def create_statistics_score_question(question: SurveyMeasure, values: list[list[int]], sub_question_missing: bool) -> StatisticalValues:
    '''Create statistical values for a score question'''
    if sub_question_missing:
        return create_statistics([], question.question_type)
    else:
        sub_question_dataframe = pd.DataFrame(values)
        cronbach_alpha = None
        if len(values) > 0 and len(values[0]) > 0:
            cronbach_alpha = pg.cronbach_alpha(sub_question_dataframe)
        final_values = []
        for i in range(len(values[0])):
            participant_values = []
            for j in range(len(values)):
                participant_values.append(values[j][i])
            final_values.append(round(statistics.fmean(participant_values)))
        statistical_values = create_statistics(
            final_values, question.question_type)
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
                    sub_question.values, question.question_type)
                measure.sub_questions.append(measure_sub_question)
        elif question.question_type == 'score_question':
            values = []
            measure.sub_questions = []
            is_sub_question_empty = False
            for sub_question in question.sub_questions:
                measure_sub_question = AnalysisSubQuestion(
                    title=sub_question.title)
                measure_sub_question.statistical_values = create_statistics(
                    sub_question.values, question.question_type)
                measure.sub_questions.append(measure_sub_question)

                sub_values = sub_question.values
                if sub_question.reverse:
                    max_value = len(question.answers.values())
                    sub_values = list(map(lambda value: abs(
                        value - (max_value + 1)), sub_values))
                values.append(sub_values)
                if len(sub_question.values) == 0:
                    is_sub_question_empty = True
            measure.statistical_values = create_statistics_score_question(
                question, values, is_sub_question_empty)
        else:
            measure.statistical_values = create_statistics(
                question.values, question.question_type)
        analysis.results.append(measure)
    return analysis


@router.get('')
def get_analyses(
    hackathons_collection: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    hackathons: str = '',
    filters: str = '[]'
) -> list[Analysis]:
    '''Create all analyses given a list of filters'''
    user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['sub']
    hackathon_ids_list = hackathons.split(',')
    hackathon = build_single_hackathon(
        hackathon_ids_list, hackathons_collection)
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
