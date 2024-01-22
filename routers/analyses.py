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
from models.Hackathon import Hackathon
import statistics
from models.Analysis import SingleAnalysisMeasure, CategoryAnalysisMeasure, Analysis

router = APIRouter()

def combine_hackathon_values(first_hackathon: dict, second_hackathon: dict):
    '''Add values of the second to the first hackathon'''
    for measure in second_hackathon:
        if second_hackathon[measure] != None:
            if type(second_hackathon[measure]) is dict:
                for sub_measure in second_hackathon[measure]:
                    if second_hackathon[measure][sub_measure] != None:
                        if first_hackathon[measure][sub_measure] != None:
                            first_hackathon[measure][sub_measure].extend(second_hackathon[measure][sub_measure])
                        else:
                            first_hackathon[measure][sub_measure] = second_hackathon[measure][sub_measure]
            else:
                if first_hackathon[measure] != None:
                    first_hackathon[measure].extend(second_hackathon[measure])
                else:
                    first_hackathon[measure] = second_hackathon[measure]


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
    for hackathon in cursor:
        if final_hackathon == None:
            final_hackathon = hackathon
        else:
            combine_hackathon_values(final_hackathon['results'], hackathon['results'])
    return final_hackathon

def combine_hackathon_values_strict(first_hackathon: dict, second_hackathon: dict):
    '''Add values of the second to the first hackathon. Remove all measures, that are not contained in both'''
    for measure in first_hackathon:
        if first_hackathon[measure] != None and second_hackathon[measure] != None:
            if type(first_hackathon[measure]) is dict:
                for sub_measure in first_hackathon[measure]:
                    if first_hackathon[measure][sub_measure] != None and second_hackathon[measure][sub_measure] != None:
                        first_hackathon[measure][sub_measure].extend(second_hackathon[measure][sub_measure])
                    else:
                        first_hackathon[measure][sub_measure] = None
            else:
                first_hackathon[measure].extend(second_hackathon[measure])
        else:
            first_hackathon[measure] = None

def build_single_hackathon(hackathon_ids: list[str], hackathons_collection: Collection) -> dict:
    '''Turn a list of hackathons into a single dataset'''
    hackathon_object_ids = [ObjectId(id) for id in hackathon_ids]
    hackathons_cursor = hackathons_collection.find({ '_id': { '$in': hackathon_object_ids } })
    final_hackathon = None
    for hackathon in hackathons_cursor:
        if final_hackathon == None:
            final_hackathon = hackathon
        else:
            combine_hackathon_values_strict(final_hackathon['results'], hackathon['results'])
    return final_hackathon

def create_statistics(values: list[str | int]) -> SingleAnalysisMeasure | CategoryAnalysisMeasure:
    ''
    participants = len(values)
    distribution = {}
    for value in values:
        value_as_string = str(value)
        if value_as_string in distribution:
            distribution[value_as_string] += 1
        else:
            distribution[value_as_string] = 1
    if type(values[0]) is int:
        deviation = statistics.stdev(values) if len(values) > 1 else 0
        return SingleAnalysisMeasure(
            participants=participants,
            average=statistics.fmean(values),
            deviation=deviation,
            distribution=distribution
        )
    else:
        return CategoryAnalysisMeasure(
            participants=participants,
            distribution=distribution
        )

def create_analysis(hackathon: dict) -> Analysis:
    '''Create an object, that contains statistical values for every measure of a survey'''
    Hackathon.model_validate(hackathon)
    statistics = {}
    hackathon_results = hackathon['results']
    for measure in hackathon_results:
        if hackathon_results[measure] != None:
            if type(hackathon_results[measure]) is dict:
                for sub_measure in hackathon_results[measure]:
                    values = hackathon_results[measure][sub_measure]
                    if values != None:
                        if measure not in statistics:
                            statistics[measure] = {}
                        statistics[measure][sub_measure] = create_statistics(hackathon_results[measure][sub_measure])
            else:
                statistics[measure] = create_statistics(hackathon_results[measure])
    analysis = dict(hackathon)
    analysis['results'] = statistics
    return Analysis.model_validate(analysis)

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
    statistics = create_analysis(hackathon)
    decoded_filters = json.loads(filters)
    filtered_statistics = []
    if len(decoded_filters) == 0:
        decoded_filters.append({})
    for filter_combination in decoded_filters:
        filtered_hackathon = build_filtered_hackathon(filter_combination, hackathons_collection)
        if filtered_hackathon != None:
            filtered_statistics.append(create_analysis(filtered_hackathon))
    return {
        'selected': statistics,
        'comparisons': filtered_statistics
    }