'''Helper script to put all hackathon csv files in a given folder into the database'''

from pymongo import MongoClient
import pandas as pd
import routers.hackathons as hack
from models.Hackathon import Hackathon
from data.survey_questions import QUESTIONS
import copy
from datetime import datetime

CONNECTION_STRING = 'mongodb://localhost:27017'
DB_NAME = 'hack-eval'
FOLDER_PATH = ''
USER_ID = ''

client = MongoClient(CONNECTION_STRING)
print('Connected to MongoDB')

database = client[DB_NAME]
hackathons = database['hackathons']

overview = pd.read_excel(f'{FOLDER_PATH}/hackathons-overview.xlsx')

for i, found_hackathon in overview.iterrows():
    hackathon_id = found_hackathon['ID']
    start_day, start_month, start_year = found_hackathon['start'].split('.')
    start = datetime(
        year=int(start_year),
        month=int(start_month),
        day=int(start_day)
    )
    end_day, end_month, end_year = found_hackathon['end'].split('.')
    end = datetime(
        year=int(end_year),
        month=int(end_month),
        day=int(end_day)
    )
    hackathon = Hackathon(
        title=hackathon_id,
        incentives=found_hackathon['incentives'],
        size=found_hackathon['size'],
        types=found_hackathon['type'].split(','),
        venue=found_hackathon['venue'],
        start=start,
        end=end,
        results=copy.deepcopy(QUESTIONS),
        created_by=USER_ID
    )
    file = pd.read_csv(f'{FOLDER_PATH}/{hackathon_id}.csv')
    hack.map_hackathon_results_csv(hackathon, file)
    hackathons.insert_one(hackathon.model_dump())
    print(f'Hackathon {hackathon_id} inserted into database')
