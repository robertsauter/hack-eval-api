'''Helpers for cleaning up survey datasets'''

import pandas as pd
from data.survey_questions import QUESTIONS
from routers.hackathons import match_question
from models.Hackathon import SurveyMeasure

TITLE_TRANSLATIONS_MAP = {
    'An wie vielen Hackathons hast du bereits teilgenommen?': 'How many hackathons have you participated in the past?',
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf deine Motivation am Hackathon teilzunehmen zu? [Spaß haben]': 'To what extent was your decision to participate in this hackathon motivated by... [Having fun]',
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf deine Motivation am Hackathon teilzunehmen zu? [An einem interessanten Projekt mitwirken]': 'To what extent was your decision to participate in this hackathon motivated by... [Working on an interesting project idea]',
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf deine Motivation am Hackathon teilzunehmen zu? [Zeit um an meinem Projekt zu arbeiten]': 'To what extent was your decision to participate in this hackathon motivated by... [Dedicated time to get work done]',
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf deine Motivation am Hackathon teilzunehmen zu? [Neue Methoden oder Fähigkeiten erlernen]': 'To what extent was your decision to participate in this hackathon motivated by... [Learning new tools or skills]',
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf deine Motivation am Hackathon teilzunehmen zu? [Neue Personen kennenlernen]': 'To what extent was your decision to participate in this hackathon motivated by... [Meeting new people]',
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf deine Motivation am Hackathon teilzunehmen zu? [Sehen woran andere arbeiten]': 'To what extent was your decision to participate in this hackathon motivated by... [Seeing what others are working on]',
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf deine Motivation am Hackathon teilzunehmen zu? [Meine Erfahrungen und Expertise mit anderen teilen]': 'To what extent was your decision to participate in this hackathon motivated by... [Sharing my experience and expertise]',
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf deine Motivation am Hackathon teilzunehmen zu? [Sich am Hackathon teilnehmenden Freunden anschließen]': 'To what extent was your decision to participate in this hackathon motivated by... [Joining friends that participate]',
    'Hattet ihr einen Teamleiter?': 'Was there a team leader?',
    'Wie gut kanntest du deine Teammitglieder vor dem Hackathon? [Ich kannte meine Teammitglieder schon sehr gut.]': 'How well did you know your team members? [I knew my team members well.]',
    'Wie gut kanntest du deine Teammitglieder vor dem Hackathon? [Ich habe schonmal mit einigen der Teammitglieder zusammen gearbeitet.]': 'How well did you know your team members? [I have collaborated with some of my team members before.]',
    'Wie gut kanntest du deine Teammitglieder vor dem Hackathon? [Ich habe meine Teammitglieder vor dem Hackathon kennengelernt. ]': 'How well did you know your team members? [I have been close to some of my team members before.]',
    'Wie gut kanntest du deine Teammitglieder vor dem Hackathon? [Ich habe mich mit meinen Teammitgliedern vor dem Hackathon getroffen.]': 'How well did you know your team members? [I have socialized with some of my team members (outside of this hackathon) before.]',
    'Wie würdest du die Zusammenarbeit im Team beschreiben? [(1) effizient bis (5) ineffizient]': 'Would you describe your team process as more... [(1) Inefficient to (5) Efficient]',
    'Wie würdest du die Zusammenarbeit im Team beschreiben? [(1) unkoordiniert bis (5) koordiniert]': 'Would you describe your team process as more... [(1) Uncoordinated to (5) Coordinated]',
    'Wie würdest du die Zusammenarbeit im Team beschreiben? [(1) unfair bis (5) fair]': 'Would you describe your team process as more... [(1) Unfair to (5) Fair]',
    'Wie würdest du die Zusammenarbeit im Team beschreiben? [(1) verwirrend bis (5) leicht verständlich]': 'Would you describe your team process as more... [(1) Confusing to (5) Easy to understand]',
    'Inwiefern stimmst du den folgenden Aussagen im Bezug auf die ZIELE deines Teams zu? [Meine Aufgaben und mein Verantwortungsbereich im Team waren für mich klar. ]': 'Please indicate your level of agreement with the following statements related to your GOALS as a team. [I was uncertain of my duties and responsibilities in this team.]',
    'Inwiefern stimmst du den folgenden Aussagen im Bezug auf die ZIELE deines Teams zu? [Die Ziele meines Team waren für mich klar.]': 'Please indicate your level of agreement with the following statements related to your GOALS as a team. [I was unclear about the goals and objectives for my work in this team.]',
    'Inwiefern stimmst du den folgenden Aussagen im Bezug auf die ZIELE deines Teams zu? [Der Zusammenhang zwischen meinen Aufgaben und den Zielen meines Teams war mir klar.]': 'Please indicate your level of agreement with the following statements related to your GOALS as a team. [I was unsure how my work relates to the overall objectives of my team.]',
    'Inwiefern stimmst du den folgenden Aussagen im Bezug auf dein TEAM zu? [Jedes Teammitglied hatte die Möglichkeit seine Meinung zu äußern.]': 'Please indicate your level of agreement with the following statements about your TEAM. [Everyone had a chance to express his/her opinion.]',
    'Inwiefern stimmst du den folgenden Aussagen im Bezug auf dein TEAM zu? [Wir haben die Ideen und Meinungen jedes Teammitglieds berücksichtigt.]': 'Please indicate your level of agreement with the following statements related to your TEAM. [The team members responded to the comments made by others.]',
    'Inwiefern stimmst du den folgenden Aussagen im Bezug auf dein TEAM zu? [Alle Teammitglieder haben sich aktiv in die Teamarbeit eingebracht.]': 'Please indicate your level of agreement with the following statements related to your TEAM. [The team members participated very actively during the project.]',
    'Inwiefern stimmst du den folgenden Aussagen im Bezug auf dein TEAM zu? [Im Großen und Ganzen hat jedes Teammitglied zum Ergebnis beigetragen.]': 'Please indicate your level of agreement with the following statements related to your TEAM. [Overall, the participation of each member in the team was effective.]',
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf deine Zufriedenheit mit deinem TEAMERGEBNIS zu? [Ich bin zufrieden mit meinem Teamergebnis.]': 'Please indicate your level of agreement with the following statements related to your SATISFACTION with your project. [I am satisfied with the work completed in my project.]',
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf deine Zufriedenheit mit deinem TEAMERGEBNIS zu? [Ich bin zufrieden mit dem Beitrag meiner Teammitglieder zu dem Teamergebnis.]': "Please indicate your level of agreement with the following statements related to your SATISFACTION with your project. [I am satisfied with the quality of my team's output.]",
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf deine Zufriedenheit mit deinem TEAMERGEBNIS zu? [Meine vorherigen Vorstellungen zu dem Teamergebnis wurden erfüllt]': 'Please indicate your level of agreement with the following statements related to your SATISFACTION with your project. [My ideal outcome coming into my project achieved.]',
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf deine Zufriedenheit mit deinem TEAMERGEBNIS zu? [Meine Erwartungen an mein Team wurden erfüllt.]': 'Please indicate your level of agreement with the following statements related to your SATISFACTION with your project. [My expectations towards my team were met.]',
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf die ZUKUNFT deines Teamergebnisses zu? [Ich bevorzuge es weiter an dem Ergebnis zu arbeiten statt es ruhen zu lassen.]': 'Please indicate your FUTURE INTENTIONS related to your hackathon project. [I intend to continue working on my hackathon project rather than not continue working on it.]',
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf die ZUKUNFT deines Teamergebnisses zu? [Ich bevorzuge es weiter an dem Ergebnis zu arbeiten statt ein anderes Projekt zu verfolgen. ]': 'Please indicate your FUTURE INTENTIONS related to your hackathon project. [My intentions are to continue working on my hackathon project rather than any other project.]',
    'Inwiefern stimmst du den folgenden Aussagen im Hinblick auf die ZUKUNFT deines Teamergebnisses zu? [Falls möglich, würde ich gerne, soweit ich kann, an dem Ergebnis weiterarbeiten.]': 'Please indicate your FUTURE INTENTIONS related to your hackathon project. [If I could, I would like to continue working on my hackathon project as much as possible.]',
    'Wie alt bist du?': 'How old are you currently?',
    'Bist du ... ?': 'Are you...?',
    'Was ist dein höchster Schulabschluss?': 'What is highest level of formal education that you have completed until now?',
    'Siehst du dich als Teil einer Minderheit? (z.B. aufgrund deiner Hautfarbe, deines Geschlechts, deiner Expertise oder aus einem anderen Grund)': 'Do you consider yourself a minority? (For example in terms of race, gender, expertise or in another way)'
}

ANSWER_TRANSLATIONS_MAP = {
    'Trifft zu': 'Completely',
    'Trifft eher zu': 'To a large extent',
    'Trifft teils zu': 'To a moderate extent',
    'Trifft eher nicht zu': 'To some extent',
    'Trifft überhaupt nicht zu': 'Not at all',
    'Ja, ich war der Teamleiter.': 'Yes, I was the team leader.',
    'Ja, ein anderes Teammitglied war der Teamleiter.': 'Yes, someone else was the team leader.',
    'Nein, wir hatten keinen eindeutigen Teamleiter.': 'No, there was no clear leader in the team.',
    'Stimme überhaupt nicht zu': 'Strongly disagree',
    'Stimme eher nicht zu': 'Somewhat disagree',
    'Neutral': 'Neither agree nor disagree',
    'Stimme eher zu': 'Somewhat agree',
    'Stimme voll und ganz zu': 'Strongly agree',
    'Zwischen 18 und 24 Jahre': '18 to 24',
    'Zwischen 25 und 34 Jahre': '25 to 34',
    'Zwischen 35 und 44 Jahre': '35 to 44',
    'Zwischen 45 und 54 Jahre': '45 to 54',
    'Zwischen 55 und 64 Jahre': '55 to 64',
    'Zwischen 65 und 74 Jahre': '65 to 74',
    'Männlich': 'Male',
    'Weiblich': 'Female',
    'Realschulabschluss': 'High school diploma or GED',
    'Abitur': 'High school diploma or GED',
    'Fachhochschule/ Universität (Bachelor)': "Bachelor's degree",
    'Fachhochschule/ Universität (Master)': "Master's degree",
    'Promotion': 'Doctorate',
    'Keine Angabe': 'Prefer not to say',
    'Nein': 'No',
    'Ja': 'Yes'
}

DISAGREE_TO_AGREE_LIST = [
    'Strongly disagree',
    'Somewhat disagree',
    'Neither agree nor disagree',
    'Somewhat agree',
    'Strongly agree'
]


def translate_file(file_path: str) -> None:
    '''Translate a file, with the defined translation maps, the result is then saved as a new file. Questions that are not found are removed'''
    file = pd.read_csv(f'{file_path}.csv')
    translated_values: dict[str, list] = {}
    for title in file:
        if title in TITLE_TRANSLATIONS_MAP:
            new_title = TITLE_TRANSLATIONS_MAP[title]
            for value in file[title]:
                new_value = ANSWER_TRANSLATIONS_MAP[value] if value in ANSWER_TRANSLATIONS_MAP else value
                if new_title in translated_values:
                    translated_values[new_title].append(new_value)
                else:
                    translated_values[new_title] = [new_value]
    result = pd.DataFrame(translated_values)
    print('Translated file')
    result.to_csv(f'{file_path}_translated.csv', index=False)
    print(f'Saved translated file in: {file_path}_translated.csv')


def invert_scales(file_path: str, scale_titles: list[str], possible_answers: list[str]) -> None:
    '''Invert values in a survey file for a given list of question titles'''
    file = pd.read_csv(f'{file_path}.csv')
    answers_length = len(possible_answers)
    for title in scale_titles:
        values = file[title]
        new_values = []
        for value in values:
            try:
                index = possible_answers.index(value)
                new_value = possible_answers[abs((index + 1) - answers_length)]
                new_values.append(new_value)
            except ValueError:
                new_values.append(value)
        file[title] = pd.Series(new_values)
    print('Inverted scales')
    file.to_csv(f'{file_path}_inverted.csv', index=False)
    print(f'Saved file with inverted scales in: {file_path}_inverted.csv')


def map_numbers_to_strings(file_path: str) -> None:
    '''For files, where string answers are saved as number: Map number values to the corresponding strings'''
    file = pd.read_csv(f'{file_path}.csv')
    for title in file:
        title_sections = title.split('[')
        question_title = title_sections[0] if len(
            title_sections) > 1 else title
        for raw_question in QUESTIONS:
            question = SurveyMeasure.model_validate(raw_question)
            if question.answer_type == 'string_to_int' and match_question(question, question_title):
                new_values = []
                for answer in file[title]:
                    new_value = None
                    for key, value in question.answers.items():
                        if answer == value:
                            new_value = key
                            break
                    new_values.append(
                        new_value if new_value != None else answer)
                file[title] = pd.Series(new_values)
                break
    print('Mapped number answers to strings')
    file.to_csv(f'{file_path}_mapped.csv', index=False)
    print(f'Saved file with mapped answers in: {file_path}_mapped.csv')
