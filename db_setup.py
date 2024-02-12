from pymongo import MongoClient
import pandas as pd
import routers.hackathons as hack
from models.Hackathon import Hackathon
from data.survey_questions import QUESTIONS
import copy

CONNECTION_STRING = 'mongodb://localhost:27017'
DB_NAME = 'hack-eval'
FOLDER_PATH = ''

client = MongoClient(CONNECTION_STRING)
print('Connected to MongoDB')

database = client[DB_NAME]
hackathons = database['hackathons']

overview = pd.read_excel(f'{FOLDER_PATH}/!hackathons-overview.xlsx')

for i, found_hackathon in overview.iterrows():
    hackathon_id = found_hackathon['ID']
    hackathon = Hackathon(
        title=hackathon_id,
        incentives=found_hackathon['incentives'],
        size=found_hackathon['size'],
        types=found_hackathon['type'].split(','),
        venue=found_hackathon['venue'],
        results=copy.deepcopy(QUESTIONS),
        created_by='65c8a97d9b5559df2bd83875'
    )
    file = pd.read_csv(f'{FOLDER_PATH}/{hackathon_id}.csv')
    hack.map_hackathon_results_csv(hackathon, file)
    hackathons.insert_one(hackathon.model_dump())
    print(f'Hackathon {hackathon_id} inserted into database')