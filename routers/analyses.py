from fastapi import APIRouter, Depends
import json
from models.Hackathon import Hackathon
from typing import Annotated
from pymongo.collection import Collection
from lib.database import hackathons_collection
from bson.objectid import ObjectId
from typing import Annotated
from lib.globals import OAUTH2_SCHEME

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
    for key in filter_combination:
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

@router.get('')
def get_analyses(
    hackathons_collection: Annotated[Collection, Depends(hackathons_collection)],
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    hackathons: str = '',
    filters: str = '{}'
):
    '''Create all analyses given a list of filters'''
    hackathon_ids_list = hackathons.split(',')
    hackathon = build_single_hackathon(hackathon_ids_list, hackathons_collection)
    encoded_filters = json.loads(filters)
    filtered_hackathons = []
    for filter_combination in encoded_filters:
        filtered_hackathons.append(build_filtered_hackathon(filter_combination, hackathons_collection))
    return ''