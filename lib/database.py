'''Database utility functions, to be used as dependencies by other modules'''

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Annotated
from fastapi import Depends

CONNECTION_STRING = 'mongodb://localhost:27017'
DB_NAME = 'hack-eval'

def database() -> Database:
    client = MongoClient(CONNECTION_STRING)
    return client[DB_NAME]

def users_collection(database: Annotated[Database, Depends(database)]) -> Collection:
    return database['users']

def hackathons_collection(database: Annotated[Database, Depends(database)]) -> Collection:
    return database['hackathons']

def filters_collection(database: Annotated[Database, Depends(database)]) -> Collection:
    return database['filters']