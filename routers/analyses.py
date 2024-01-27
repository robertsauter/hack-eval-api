from fastapi import APIRouter, Depends
import json
from typing import Annotated
from pymongo.collection import Collection
from lib.database import hackathons_collection
from bson.objectid import ObjectId
from typing import Annotated
from lib.globals import OAUTH2_SCHEME
from models.Filter import Filter
from lib.http_exceptions import HTTP_422
from models.Hackathon import Hackathon, SurveyMeasure
import statistics
from models.Analysis import Analysis, StatisticalValues, AnalysisMeasure, AnalysisSubQuestion

router = APIRouter()

def build_filtered_hackathon(filter_combination: dict, hackathons_collection: Collection):
    '''Create a single dataset, that combines the hackathons, that were found from the filter combination'''
    filter_values = {}
    try:
        Filter.model_validate(filter_combination)
    except:
        HTTP_422('Filter combination is invalid')
    for key in filter_combination:
        if key != 'name' and len(filter_combination[key]) != 0:
            if key == 'types':
                filter_values[key] = { '$elemMatch': { "$in": filter_combination[key] } }
            else:
                filter_values[key] = { '$in': filter_combination[key] }
    cursor = hackathons_collection.find(filter_values)
    final_hackathon = None
    for hackathon_dict in cursor:
        hackathon = Hackathon.model_validate(hackathon_dict)
        if final_hackathon == None:
            final_hackathon = hackathon
        else:
            combine_hackathon_values(final_hackathon.results, hackathon.results, False)
    if final_hackathon != None:
        name = filter_combination['name'] if 'name' in filter_combination else 'All hackathons'
        final_hackathon.title = name
    return final_hackathon

def extend_values(first: list[int | str], second: list[int | str], strict: bool):
    '''Extend an array with a second one. If strict flag is set, remove all values if one of the arrays is empty'''
    if strict:
        if len(first) != 0 and len(second) != 0:
            first.extend(second)
        else:
            first.clear()
    else:
        first.extend(second)

def combine_hackathon_values(first_hackathon: list[SurveyMeasure], second_hackathon: list[SurveyMeasure], strict: bool):
    '''Add values of the second to the first hackathon. Remove all measures, that are not contained in both'''
    for i in range(len(first_hackathon)):
        if first_hackathon[i].question_type == 'group_question':
            for j in range(len(first_hackathon[i].sub_questions)):
                extend_values(first_hackathon[i].sub_questions[j].values, second_hackathon[i].sub_questions[j].values, strict)
        else:
            extend_values(first_hackathon[i].values, second_hackathon[i].values, strict)

def build_single_hackathon(hackathon_ids: list[str], hackathons_collection: Collection):
    '''Turn a list of hackathons into a single dataset'''
    hackathon_object_ids = [ObjectId(id) for id in hackathon_ids]
    hackathons_cursor = hackathons_collection.find({ '_id': { '$in': hackathon_object_ids } })
    final_hackathon = None
    for hackathon_dict in hackathons_cursor:
        hackathon = Hackathon.model_validate(hackathon_dict)
        if final_hackathon == None:
            final_hackathon = hackathon
        else:
            combine_hackathon_values(final_hackathon.results, final_hackathon.results, True)
    return final_hackathon
    
def create_statistics(values: list[int | str], question_type: str):
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

def create_analysis(hackathon: Hackathon):
    '''Create an object, that contains statistical values for every measure of a survey'''
    analysis = Analysis(
        title=hackathon.title,
        incentives=hackathon.incentives,
        venue=hackathon.venue,
        size=hackathon.size,
        types=hackathon.types,
        link=hackathon.link
        )
    for question in hackathon.results:
        measure = AnalysisMeasure(
            title=question.title,
            question_type=question.question_type,
            answer_type=question.answer_type
        )
        if question.question_type == 'group_question':
            measure.sub_questions = []
            for sub_question in question.sub_questions:
                measure_sub_question = AnalysisSubQuestion(title=sub_question.title)
                measure_sub_question.statistical_values = create_statistics(sub_question.values, question.question_type)
                measure.sub_questions.append(measure_sub_question)
        else:
            measure.statistical_values = create_statistics(question.values, question.question_type)
        analysis.results.append(measure)
    return analysis

@router.get('')
def get_analyses(
    hackathons_collection: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    hackathons: str = '',
    filters: str = '[]'
):
    '''Create all analyses given a list of filters'''
    hackathon_ids_list = hackathons.split(',')
    hackathon = build_single_hackathon(hackathon_ids_list, hackathons_collection)
    analyses = [create_analysis(hackathon)]
    decoded_filters = json.loads(filters)
    if len(decoded_filters) == 0:
        decoded_filters.append({})
    for filter_combination in decoded_filters:
        filtered_hackathon = build_filtered_hackathon(filter_combination, hackathons_collection)
        if filtered_hackathon != None:
            analyses.append(create_analysis(filtered_hackathon))
    return analyses