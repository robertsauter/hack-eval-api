NOTATALL_TO_COMPLETELY = {
    'Not at all': 1,
    'To some extent': 2,
    'To a moderate extent': 3,
    'To a large extent': 4,
    'Completely': 5
}

DISAGREE_TO_AGREE = {
    'Strongly disagree': 1,
    'Somewhat disagree': 2,
    'Neither agree nor disagree': 3,
    'Somewhat agree': 4,
    'Strongly agree': 5
}

SESSIONS = [
    {
        'title': 'Pre-event webinar',
        'values': []
    },
    {
        'title': 'Checkpoints',
        'values': []
    },
    {
        'title': 'Mentoring sessions',
        'values': []
    }
]

QUESTIONS = [
    {
        'title': 'To what extent was your decision to participate in this hackathon motivated by...',
        'question_type': 'group_question',
        'answer_type': 'string_to_int',
        'sub_questions': [
            {
                'title': 'Having fun',
                'values': []
            },
            {
                'title': 'Making something cool / Working on an interesting project idea',
                'values': []
            },
            {
                'title': 'Learning new tools or skills',
                'values': []
            },
            {
                'title': 'Meeting new people',
                'values': []
            },
            {
                'title': 'Seeing what others are working on',
                'values': []
            },
            {
                'title': 'Sharing my experience and expertise',
                'values': []
            },
            {
                'title': 'Joining friends that participate',
                'values': []
            },
            {
                'title': 'Dedicated time to get work done',
                'values': []
            },
            {
                'title': 'Win a prize',
                'values': []
            }
        ],
        'answers': NOTATALL_TO_COMPLETELY
    },
    {
        'title': 'How many hackathons have you participated in the past?',
        'question_type': 'single_question',
        'answer_type': 'int',
        'values': []
    },
    {
        'title': 'How many people were in your team (including yourself)?',
        'question_type': 'single_question',
        'answer_type': 'int',
        'values': []
    },
    {
        'title': 'Was there a team leader?',
        'question_type': 'category_question',
        'answer_type': 'string',
        'answers': [
            'Yes, I was the team leader.',
            'Yes, someone else was the team leader.',
            'No, there was no clear leader in the team.'
        ],
        'values': []
    },
    {
        'title': 'Was there a project manager?',
        'question_type': 'category_question',
        'answer_type': 'string',
        'answers': [
            'Yes, I was the project manager.',
            'Yes, someone else was the project manager.',
            'No, there was no clear project manager in the team.'
        ],
        'values': []
    },
    {
        'title': 'Was there a social-emotional leader?',
        'question_type': 'category_question',
        'answer_type': 'string',
        'answers': [
            'Yes, I was the social-emotional leader.',
            'Yes, someone else was the social-emotional leader.',
            'No, there was no clear social-emotional in the team.'
        ],
        'values': []
    },
    {
        'title': 'How well did you know your team members?',
        'question_type': 'score_question',
        'answer_type': 'string_to_int',
        'sub_questions': [
            'I knew my team members well.',
            'I have collaborated with some of my team members before.',
            'I have been close to some of my team members before.',
            'I have socialized with some of my team members (outside of this hackathon) before.'
        ],
        'answers': DISAGREE_TO_AGREE,
        'values': []
    },
    {
        'title': 'Would you describe your team process as more...',
        'question_type': 'score_question',
        'answer_type': 'int',
        'sub_questions': [
            '(1) Inefficient to (5) Efficient',
            '(1) Uncoordinated to (5) Coordinated',
            '(1) Unfair to (5) Fair',
            '(1) Confusing to (5) Easy to understand'
        ],
        'values': []
    },
    {
        'title': 'Please indicate your level of agreement with the following statements related to your GOALS as a team.',
        'question_type': 'score_question',
        'answer_type': 'string_to_int',
        'sub_questions': [
            'I was uncertain of my duties and responsibilities in this team.',
            'I was unclear about the goals and objectives for my work in this team.',
            'I was unsure how my work relates to the overall objectives of my team.',
        ],
        'answers': DISAGREE_TO_AGREE,
        'values': []
    },
    {
        'title': 'Please indicate your level of agreement with the following statements about your TEAM.',
        'question_type': 'score_question',
        'answer_type': 'string_to_int',
        'sub_questions': [
            'Everyone had a chance to express his/her opinion.',
            'The team members responded to the comments made by others.',
            'The team members participated very actively during the project.',
            'Overall, the participation of each member in the team was effective.'
        ],
        'answers': DISAGREE_TO_AGREE,
        'values': []
    },
    {
        'title': 'Please indicate your level of agreement with the following statements related to your SATISFACTION with your project.',
        'question_type': 'score_question',
        'answer_type': 'string_to_int',
        'sub_questions': [
            'I am satisfied with the work completed in my project.',
            "I am satisfied with the quality of my team's output.",
            'My ideal outcome coming into my project achieved.',
            'My expectations towards my team were met.'
        ],
        'answers': DISAGREE_TO_AGREE,
        'values': []
    },
    {
        'title': 'Please indicate your level of agreement with the following statements related to the USEFULNESS of your project.',
        'question_type': 'score_question',
        'answer_type': 'string_to_int',
        'sub_questions': [
            'My project improves my performance during my everyday work.',
            'My project improves my productivity during my everyday work.',
            'My project improves my effectiveness during my everyday work.',
            'Overall, my project will be useful during my everyday work.'
        ],
        'answers': DISAGREE_TO_AGREE,
        'values': []
    },
    {
        'title': 'Please indicate your FUTURE INTENTIONS related to your hackathon project.',
        'question_type': 'score_question',
        'answer_type': 'string_to_int',
        'sub_questions': [
            'I intend to continue working on my hackathon project rather than not continue working on it.',
            'My intentions are to continue working on my hackathon project rather than any other project.',
            'If I could, I would like to continue working on my hackathon project as much as possible.',
        ],
        'answers': DISAGREE_TO_AGREE,
        'values': []
    },
    {
        'title': 'Please indicate your level of agreement with the following statements related to your ABILITY to continue working on your hackathon project.',
        'question_type': 'score_question',
        'answer_type': 'string_to_int',
        'sub_questions': [
            'I would be able to continue working on my hackathon project.',
            'Continuing to work on my hackathon project is entirely under my control.',
            'I have the resources, knowledge, and ability to continue working on my project after the hackathon.',
        ],
        'answers': DISAGREE_TO_AGREE,
        'values': []
    },
    {
        'title': 'To what extent do you agree with the following statements about THE SUPPORT THE MENTORS PROVIDED during this hackathon?',
        'question_type': 'group_question',
        'answer_type': 'string_to_int',
        'sub_questions': [
            {
                'title': 'The mentors supported us to scope our project.',
                'values': []
            },
            {
                'title': 'The mentors took decisions about the direction of our project.',
                'values': []
            },
            {
                'title': 'The mentors provided us with solutions to technical problems we encountered.',
                'values': []
            },
            {
                'title': 'The mentors helped us to find our own solutions to technical problems we encountered.',
                'values': []
            },
            {
                'title': 'The mentor were mainly focused on our learning progress.',
                'values': []
            },
            {
                'title': 'The mentors were mainly focused on our project progress.',
                'values': []
            },
            {
                'title': 'The mentors were part of our team.',
                'values': []
            },
            {
                'title': 'The mentors showed interest in us beyond the project we were working on.',
                'values': []
            },
            {
                'title': 'We could reach the mentors when we needed help.',
                'values': []
            }
        ],
        'answers': DISAGREE_TO_AGREE,
    },
    {
        'title': 'How do you feel about your OVERALL EXPERIENCE participating in this hackathon?',
        'question_type': 'score_question',
        'answer_type': 'int',
        'sub_questions': [
            '(1) Very dissatisfied to (5) Very satisfied',
            '(1) Very displeased to (5) Very pleased',
            '(1) Very frustrated to (5) Very contented',
            '(1) Absolutely terrible to (5) Absolutely delighted',
        ],
        'values': []
    },
    {
        'title': 'Do people identify with the community?',
        'question_type': 'score_question',
        'answer_type': 'string_to_int',
        'sub_questions': [
            'I identify with other members of this community.',
            'I am like other members of this community.',
            'This community is an important reflection of who I am.',
            'I would like to continue working with this community.',
            'I dislike being a member of this community.',
            'I would rather belong to another community.'
        ],
        'answers': DISAGREE_TO_AGREE,
        'values': []
    },
    {
        'title': 'Do you plan to participate in a similar event in the future?',
        'question_type': 'single_question',
        'answer_type': 'string_to_int',
        'answers': {
            'Definitely not': 1,
            'Probably not': 2,
            'Might of might not': 3,
            'Probably yes': 4,
            'Definitely yes': 5
        },
        'values': []
    },
    {
        'title': 'How likely would you recommend a similar hackathon to a friend or colleague?',
        'question_type': 'single_question',
        'answer_type': 'int',
        'values': []
    },
    {
        'title': 'Please rate how SATISFIED you were with the following sessions.',
        'question_type': 'group_question',
        'answer_type': 'string_to_int',
        'sub_questions': SESSIONS,
        'answers': NOTATALL_TO_COMPLETELY,
    },
    {
        'title': 'Please rate how USEFUL you found the following sessions.',
        'question_type': 'group_question',
        'answer_type': 'string_to_int',
        'sub_questions': SESSIONS,
        'answers': {
            'Not useful': 1,
            'Slightly useful': 2,
            'Moderately useful': 3,
            'Useful': 4,
            'Very useful': 5
        }
    },
    {
        'title': 'Please rate how ENJOYABLE you found the following sessions.',
        'question_type': 'group_question',
        'answer_type': 'string_to_int',
        'sub_questions': SESSIONS,
        'answers': {
            'Not enjoyable': 1,
            'Slightly enjoyable': 2,
            'Moderately enjoyable': 3,
            'Enjoyable': 4,
            'Very enjoyable': 5
        }
    },
    {
        'title': 'How many years of programming experience do you have?',
        'question_type': 'single_question',
        'answer_type': 'int',
        'values': []
    },
    {
        'title': 'Referring back to the people you collaborated with at this hackathon, how do you estimate your programming experience compared to them?',
        'question_type': 'single_question',
        'answer_type': 'string_to_int',
        'answers': {
            'Very inexperienced': 1,
            'Inexperienced': 2,
            'Comparable': 3,
            'Experienced': 4,
            'Very experienced': 5
        },
        'values': []
    },
    {
        'title': 'To what extend do you agree with the following statements about your ABILITY to use these technologies?',
        'question_type': 'group_question',
        'answer_type': 'string_to_int',
        'sub_questions': [
            {
                'title': 'I am able to write some parts of programs in JAVA.',
                'values': []
            },
            {
            
                'title': 'I am able to write some parts of programs in JAVASCRIPT.',
                'values': []
            },
            {
            
                'title': 'I am able to write some parts of programs in PYTHON.',
                'values': []
            },
            {
            
                'title': 'I am able to write some parts of programs in HTML/HTML5.',
                'values': []
            },
            {
            
                'title': 'I am able to write some parts of programs in DJANGO/AIRAVATA.',
                'values': []
            },
            {
            
                'title': 'I can make some use of REQUESTS, JSON and XML.',
                'values': []
            },
            {
            
                'title': 'I can make some use of JUPYTER NOTEBOOKS.',
                'values': []
            }
        ],
        'answers': DISAGREE_TO_AGREE
    },
    {
        'title': 'To what extend do you agree with the following statements about your LEVEL OF COMFORT using these technologies?',
        'question_type': 'group_question',
        'answer_type': 'string_to_int',
        'sub_questions': [
            {
                'title': 'I am comfortable to write programs in JAVA.',
                'values': []
            },
            {
            
                'title': 'I am comfortable to write programs in JAVASCRIPT.',
                'values': []
            },
            {
            
                'title': 'I am comfortable to write programs in PYTHON.',
                'values': []
            },
            {
            
                'title': 'I am comfortable to write programs in HTML/HTML5.',
                'values': []
            },
            {
            
                'title': 'I am comfortable to write programs in DJANGO/AIRAVATA.',
                'values': []
            },
            {
            
                'title': 'I am comfortable to use REQUESTS, JSON and XML.',
                'values': []
            },
            {
            
                'title': 'I am comfortable to use JUPYTER NOTEBOOKS.',
                'values': []
            }
        ],
        'answers': DISAGREE_TO_AGREE
    },
    {
        'title': 'How old are you currently?',
        'question_type': 'category_question',
        'answer_type': 'string',
        'answers': [
            '18 to 24',
            '25 to 34',
            '35 to 44',
            '45 to 54',
            '55 to 64',
            '65 to 74',
            '75 or older',
            'Prefer not to say'
        ],
        'values': []
    },
    {
        'title': 'Are you...?',
        'question_type': 'category_question',
        'answer_type': 'string',
        'answers': [
            'Female',
            'Male',
            'Non-binary',
            'Prefer not to say'
        ],
        'values': []
    },
    {
        'title': 'What is highest level of formal education that you have completed until now?',
        'question_type': 'category_question',
        'answer_type': 'string',
        'answers': [
            'High school diploma or GED',
            'Some college',
            "Associate and/or bachelor's degree",
            "Bachelor's degree",
            'Professional degree',
            "Master's degree",
            'Doctorate',
            'Prefer not to say'
        ],
        'values': []
    },
    {
        'title': 'Do you consider yourself a minority? (For example in terms of race, gender, expertise or in another way)',
        'question_type': 'category_question',
        'answer_type': 'string',
        'answers': [
            'Yes',
            'No',
            'Prefer not to say'
        ],
        'values': []
    }
]