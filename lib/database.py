'''Database utility functions, to be used as dependencies by other modules'''

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Annotated
from fastapi import Depends
from globals import DB_CONNECTION

DB_NAME = 'hack-eval'

def database() -> Database:
    client = MongoClient(DB_CONNECTION)
    return client[DB_NAME]

def users_collection(database: Annotated[Database, Depends(database)]) -> Collection:
    return database['users']

def hackathons_collection(database: Annotated[Database, Depends(database)]) -> Collection:
    return database['hackathons']

def filters_collection(database: Annotated[Database, Depends(database)]) -> Collection:
    return database['filters']