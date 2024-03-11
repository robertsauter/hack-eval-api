'''Helper scripts to search the data for not identified questions and suggest keywords'''

import re
from nltk.corpus import stopwords
import pandas as pd
from thefuzz import fuzz
from models.Hackathon import SurveyMeasure, Hackathon
from data.survey_questions import QUESTIONS
import nltk.corpus
nltk.download('stopwords')

FOLDER_PATH = ''
SIMILARITY = 85
STOP_WORDS = stopwords.words('english')


def find_matches_with_keywords(title: str) -> list[str]:
    '''Go through all questions and subquestions to find matching question titles by using keyword regexes'''
    matched_questions = []
    for raw_question in QUESTIONS:
        question = SurveyMeasure.model_validate(raw_question)
        pattern = re.compile(question.keywords, re.IGNORECASE)
        matching: bool = pattern.search(title) != None
        if matching:
            matched_questions.append(question.title)
        if question.question_type == 'group_question' or question.question_type == 'score_question':
            for sub_question in question.sub_questions:
                sub_pattern = re.compile(sub_question.keywords, re.IGNORECASE)
                sub_matching: bool = sub_pattern.search(title) != None
                if sub_matching:
                    matched_questions.append(sub_question.title)
    return matched_questions


def find_matches_fuzzy(title: str) -> list[str]:
    '''Go through all questions and subquestions to find matching question titles by fuzzy string matching'''
    matched_questions = []

    for raw_question in QUESTIONS:
        question = SurveyMeasure.model_validate(raw_question)
        if fuzz.ratio(title, question.title) > SIMILARITY:
            matched_questions.append(question.title)
        if question.question_type == 'group_question' or question.question_type == 'score_question':
            for sub_question in question.sub_questions:
                if fuzz.ratio(title, sub_question.title) > SIMILARITY:
                    matched_questions.append(sub_question.title)
    return matched_questions


def find_matches(hackathon: str, title: str) -> list[str]:
    '''Find questions in the defined list of questions, that are similar to the input question'''
    matches = find_matches_with_keywords(title)

    if len(matches) == 0:
        # If not matches are found with keywords, use fuzzy matching
        matches = find_matches_fuzzy(title)
        if len(matches) == 0:
            regex = generate_keywords_regex(title)
            print(f'Created regex for question "{title}": {regex}')
        elif len(matches) > 1:
            print(
                f'Question "{title}" of hackathon "{hackathon}" matched multiple questions with fuzzy matching: {"; ".join(matches)}')
    elif len(matches) > 1:
        print(
            f'Question "{title}" of hackathon "{hackathon}" matched multiple questions with keywords: {"; ".join(matches)}')


def generate_keywords_regex(title: str) -> str:
    '''Generate a regex, that matches for all words of a title, with stopwords removed'''
    # Turn lowercase
    title = title.lower()
    # Create array of words
    words = title.split(' ')
    # Remove characters that are not alphanumeric
    for i in range(len(words)):
        words[i] = ''.join(char for char in words[i] if char.isalpha())
    # Remove stopwords
    words = [word for word in words if word not in STOP_WORDS]
    # Return regex that checks for all words
    return ''.join(f'(?=.*{word})' for word in words)


def generate_keywords_for_all_hackathons():
    '''Iterate over all hackathons in the defined folder'''
    overview = pd.read_excel(f'{FOLDER_PATH}/!hackathons-overview.xlsx')
    for i, found_hackathon in overview.iterrows():
        generate_keywords_for_single_hackathon(found_hackathon['ID'])


def generate_keywords_for_single_hackathon(hackathon_id: str):
    '''Generate keyword regexes for all questions of a hackathon, that are not identified by the existing keywords or fuzzy string matching of the titles'''
    print(
        f'-----------------------------Hackathon ID: {hackathon_id}----------------------------------')
    file = pd.read_csv(f'{FOLDER_PATH}/{hackathon_id}.csv')
    for title in file.keys():
        # If the title contains square brackets, this is a subquestion
        if '[' in title:
            title_sections = title.split('[')
            question_title = title_sections[0]

            # Handle question title
            find_matches(hackathon_id, question_title)

            # Handle subquestion title
            subquestion_title = title_sections[1].split(']')[0]
            find_matches(hackathon_id, subquestion_title)
        # If not, this is a single question
        else:
            find_matches(hackathon_id, title)


def generate_keywords_for_questions():
    '''Generate list of questions with regexes as keywords for all questions. This was used to generate the initial keywords for all questions'''
    questions: list[SurveyMeasure] = []
    for raw_question in QUESTIONS:
        question = SurveyMeasure.model_validate(raw_question)
        regex = generate_keywords_regex(question.title)
        question.keywords = regex
        if question.sub_questions != None:
            for sub_question in question.sub_questions:
                sub_regex = generate_keywords_regex(sub_question.title)
                sub_question.keywords = sub_regex
        questions.append(question)
    hackathon = Hackathon(
        title='',
        incentives='competitive',
        venue='hybrid',
        size='large',
        types=['prototype'],
        results=questions,
        created_by=''
    )
    print(hackathon.model_dump_json())


generate_keywords_for_single_hackathon('2017-h1')
