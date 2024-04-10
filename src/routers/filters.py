'''Routes for handling filter presets'''

from fastapi import APIRouter, Depends
from typing import Annotated
from src.lib.globals import OAUTH2_SCHEME, SECRET_KEY, ALGORITHM
from pymongo.collection import Collection
from src.lib.database import filters_collection
from src.models.Filter import Filter, FilterWithId
from jose import jwt
from bson import ObjectId

router = APIRouter()


@router.post('')
def save_filter_combination(
    filter: Filter,
    filters_collection: Annotated[Collection, Depends(filters_collection)],
    token: Annotated[str, Depends(OAUTH2_SCHEME)]
) -> Filter:
    '''Save a filter combination in the database'''
    user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['sub']
    filter_dict = filter.model_dump()
    filter_dict['created_by'] = user_id
    filters_collection.insert_one(filter_dict)
    return filter


@router.get('')
def get_filters_by_user_id(
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    filters_collection: Annotated[Collection, Depends(filters_collection)]
) -> list[FilterWithId]:
    '''Get all saved filter combinations of the logged in user'''
    user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['sub']
    found_filters = []
    for filter in filters_collection.find({'created_by': user_id}):
        found_filters.append(FilterWithId(
            id=str(filter['_id']),
            name=filter['name'],
            incentives=filter['incentives'],
            venue=filter['venue'],
            size=filter['size'],
            types=filter['types'],
            onlyOwn=filter['onlyOwn']
        ))
    return found_filters


@router.delete('/{filter_id}')
def delete_filter(
    filter_id: str,
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    filters_collection: Annotated[Collection, Depends(filters_collection)]
) -> str:
    '''Delete the filter combination with the given id'''
    filters_collection.delete_one({'_id': ObjectId(filter_id)})
    return 'Success'
