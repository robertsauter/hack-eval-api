from models.Hackathon import LeaderMeasure, Age, Gender, Minority, Education

ANSWERS_MAP = {
    'motivation': {
        'Not at all': 1,
        'To some extent': 2,
        'To a moderate extent': 3,
        'To a large extent': 4,
        'Completely': 5
    },
    'session_satisfaction': {
        'Not at all': 1,
        'To some extent': 2,
        'To a moderate extent': 3,
        'To a large extent': 4,
        'Completely': 5
    },
    'team_leader': {
        'Yes, I was the team leader.': LeaderMeasure.YES.value,
        'Yes, someone else was the team leader.': LeaderMeasure.YES_OTHER.value,
        'No, there was no clear leader in the team.': LeaderMeasure.NO.value
    },
    'team_manager': {
        'Yes, I was the project manager.': LeaderMeasure.YES.value,
        'Yes, someone else was the project manager.': LeaderMeasure.YES_OTHER.value,
        'No, there was no clear project manager in the team.': LeaderMeasure.NO.value
    },
    'social_leader': {
        'Yes, I was the social-emotional leader.': LeaderMeasure.YES.value,
        'Yes, someone else was the social-emotional leader.': LeaderMeasure.YES_OTHER.value,
        'No, there was no clear social-emotional in the team.': LeaderMeasure.NO.value
    },
    'team_familiarity': {
        'Strongly disagree': 1,
        'Somewhat disagree': 2,
        'Neither agree nor disagree': 3,
        'Somewhat agree': 4,
        'Strongly agree': 5
    },
    'goal_clarity': {
        'Strongly disagree': 1,
        'Somewhat disagree': 2,
        'Neither agree nor disagree': 3,
        'Somewhat agree': 4,
        'Strongly agree': 5
    },
    'voice': {
        'Strongly disagree': 1,
        'Somewhat disagree': 2,
        'Neither agree nor disagree': 3,
        'Somewhat agree': 4,
        'Strongly agree': 5
    },
    'satisfaction_with_outcome': {
        'Strongly disagree': 1,
        'Somewhat disagree': 2,
        'Neither agree nor disagree': 3,
        'Somewhat agree': 4,
        'Strongly agree': 5
    },
    'perceived_usefulness': {
        'Strongly disagree': 1,
        'Somewhat disagree': 2,
        'Neither agree nor disagree': 3,
        'Somewhat agree': 4,
        'Strongly agree': 5
    },
    'programming_ability': {
        'Strongly disagree': 1,
        'Somewhat disagree': 2,
        'Neither agree nor disagree': 3,
        'Somewhat agree': 4,
        'Strongly agree': 5
    },
    'programming_comfort': {
        'Strongly disagree': 1,
        'Somewhat disagree': 2,
        'Neither agree nor disagree': 3,
        'Somewhat agree': 4,
        'Strongly agree': 5
    },
    'satisfaction_with_process': {
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5
    },
    'mentoring_experience': {
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5
    },
    'satisfaction_with_hackathon': {
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5
    },
    'continuation_intentions': {
        'Not applicable': 0,
        'Strongly disagree': 1,
        'Somewhat disagree': 2,
        'Neither agree nor disagree': 3,
        'Somewhat agree': 4,
        'Strongly agree': 5
    },
    'behavioral_control': {
        'Not applicable': 0,
        'Strongly disagree': 1,
        'Somewhat disagree': 2,
        'Neither agree nor disagree': 3,
        'Somewhat agree': 4,
        'Strongly agree': 5
    },
    'future_participation_intentions': {
        'Definitely not': 1,
        'Probably not': 2,
        'Might of might not': 3,
        'Probably yes': 4,
        'Definitely yes': 5
    },
    'recommendation_likeliness': {
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        '10': 10
    },
    'session_usefulness': {
        'Not useful': 1,
        'Slightly useful': 2,
        'Moderately useful': 3,
        'Useful': 4,
        'Very useful': 5
    },
    'session_enjoyment': {
        'Not enjoyable': 1,
        'Slightly enjoyable': 2,
        'Moderately enjoyable': 3,
        'Enjoyable': 4,
        'Very enjoyable': 5
    },
    'programming_experience_comparison': {
        'Very inexperienced': 1,
        'Inexperienced': 2,
        'Comparable': 3,
        'Experienced': 4,
        'Very experienced': 5
    },
    'age': {
        '18 to 24': Age.EIGHTEEN.value,
        '25 to 34': Age.TWENTYFIVE.value,
        '35 to 44': Age.THIRTYFIVE.value,
        '45 to 54': Age.FOURTYFIVE.value,
        '55 to 64': Age.FIFTYFIVE.value,
        '65 to 74': Age.SIXTYFIVE.value,
        '75 or older': Age.SEVENTYFIVE.value,
        'Prefer not to say': Age.PREFER_NOT_TO_SAY.value
    },
    'gender': {
        'Female': Gender.FEMALE.value,
        'Male': Gender.MALE.value,
        'Non-binary': Gender.NON_BINARY.value,
        'Prefer not to say': Gender.PREFER_NOT_TO_SAY.value
    },
    'education': {
        'High school diploma or GED': Education.HIGH_SCHOOL.value,
        'Some college': Education.COLLEGE.value,
        "Associate and/or bachelor's degree": Education.ASSOCIATE.value,
        "Bachelor's degree": Education.BACHELOR.value,
        'Professional degree': Education.PROFESSIONAL.value,
        "Master's degree": Education.MASTER.value,
        'Doctorate': Education.DOCTOR.value,
        'Prefer not to say': Education.PREFER_NOT_TO_SAY.value
    },
    'minority': {
        'Yes': Minority.YES.value,
        'No': Minority.NO.value,
        'Prefer not to say': Minority.PREFER_NOT_TO_SAY.value
    }
}

QUESTION_TITLES_MAP = {
    'To what extent was your decision to participate in this hackathon motivated by...': 'motivation',
    'Having fun': 'having_fun',
    'Making something cool / Working on an interesting project idea': 'making_something_cool',
    'Dedicated time to get work done': 'learning_new_tools',
    'Meeting new people': 'meeting_new_people',
    'Seeing what others are working on': 'seeing_what_others_are_working_on',
    'Sharing my experience and expertise': 'sharing_my_experience',
    'Joining friends that participate': 'joining_friends',
    'Win a prize': 'win_a_prize',
    'How many hackathons have you participated in the past?': 'event_participation',
    'How many people were in your team (including yourself)?': 'team_size',
    'Was there a team leader?': 'team_leader',
    'Was there a project manager?': 'team_manager',
    'Was there a social-emotional leader?': 'social_leader',
    'How well did you know your team members?': 'team_familiarity',
    'Would you describe your team process as more...': 'satisfaction_with_process',
    'Please indicate your level of agreement with the following statements related to your GOALS as a team.': 'goal_clarity',
    'Please indicate your level of agreement with the following statements about your TEAM.': 'voice',
    'Please indicate your level of agreement with the following statements related to your SATISFACTION with your project.': 'satisfaction_with_outcome',
    'Please indicate your level of agreement with the following statements related to the USEFULNESS of your project.': 'perceived_usefulness',
    'Please indicate your FUTURE INTENTIONS related to your hackathon project.': 'continuation_intentions',
    'Please indicate your level of agreement with the following statements related to your ABILITY to continue working on your hackathon project.': 'behavioral_control',
    'To what extent do you agree with the following statements about THE SUPPORT THE MENTORS PROVIDED during this hackathon?': 'mentoring_experience',
    'How do you feel about your OVERALL EXPERIENCE participating in this hackathon?': 'satisfaction_with_hackathon',
    'Do you plan to participate in a similar event in the future?': 'future_participation_intentions',
    'How likely would you recommend a similar hackathon to a friend or colleague?': 'recommendation_likeliness',
    'How SATISFIED are you with the following aspects of the hackathon?': 'session_satisfaction',
    'Please rate how USEFUL you found the following sessions.': 'session_usefulness',
    'Please rate how ENJOYABLE you found the following sessions.': 'session_enjoyment',
    'How many years of programming experience do you have?': 'programming_experience_years',
    'Referring back to the people you collaborated with at this hackathon, how do you estimate your programming experience compared to them?': 'programming_experience_comparison',
    'To what extend do you agree with the following statements about your ABILITY to use these technologies?': 'programming_ability',
    'To what extend do you agree with the following statements about your LEVEL OF COMFORT using these technologies?': 'programming_comfort',
    'How old are you currently?': 'age',
    'Are you...?': 'gender',
    'What is highest level of formal education that you have completed until now?': 'education',
    'Do you consider yourself a minority? (For example in terms of race, gender, expertise or in another way)': 'minority'
}

SPECIAL_QUESTION_TITLES_SET = {
    'To what extent was your decision to participate in this hackathon motivated by...',
    'To what extent do you agree with the following statements about THE SUPPORT THE MENTORS PROVIDED during this hackathon?',
    'How SATISFIED are you with the following aspects of the hackathon?',
    'Please rate how USEFUL you found the following sessions.',
    'Please rate how ENJOYABLE you found the following sessions.',
    'To what extend do you agree with the following statements about your ABILITY to use these technologies?',
    'To what extend do you agree with the following statements about your LEVEL OF COMFORT using these technologies?'
}