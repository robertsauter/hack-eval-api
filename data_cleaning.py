import pandas as pd
from thefuzz import fuzz
from models.Hackathon import SurveyMeasure, Hackathon
#import nltk.corpus
#nltk.download('stopwords')
from nltk.corpus import stopwords
import re

QUESTIONS = [
  {
    "title": "To what extent was your decision to participate in this hackathon motivated by...",
    "question_type": "group_question",
    "answer_type": "string_to_int",
    "sub_questions": [
      {
        "title": "Having fun",
        "values": [],
        "keywords": "(?=.*having)(?=.*fun)|(?=.*have)(?=.*fun)"
      },
      {
        "title": "Making something cool / Working on an interesting project idea",
        "values": [],
        "keywords": "(?=.*making)(?=.*something)(?=.*cool)|(?=.*working)(?=.*interesting)(?=.*project)"
      },
      {
        "title": "Learning new tools or skills",
        "values": [],
        "keywords": "(?=.*learning)(?=.*new)(?=.*tools)(?=.*skills)|(?=.*learn)(?=.*try)(?=.*something)(?=.*new)"
      },
      {
        "title": "Meeting new people",
        "values": [],
        "keywords": "(?=.*meeting)(?=.*new)(?=.*people)"
      },
      {
        "title": "Seeing what others are working on",
        "values": [],
        "keywords": "(?=.*seeing)(?=.*others)(?=.*working)"
      },
      {
        "title": "Sharing my experience and expertise",
        "values": [],
        "keywords": "(?=.*sharing)(?=.*experience)(?=.*expertise)"
      },
      {
        "title": "Joining friends that participate",
        "values": [],
        "keywords": "(?=.*joining)(?=.*friends)(?=.*participate)"
      },
      {
        "title": "Dedicated time to get work done",
        "values": [],
        "keywords": "(?=.*dedicated)(?=.*time)(?=.*get)(?=.*work)(?=.*done)|(?=.*get)(?=.*something)(?=.*done)"
      },
      {
        "title": "Win a prize",
        "values": [],
        "keywords": "(?=.*win)(?=.*prize)|(?=.*winning)"
      }
    ],
    "answers": {
      "Not at all": 1,
      "To some extent": 2,
      "To a moderate extent": 3,
      "To a large extent": 4,
      "Completely": 5
    },
    "keywords": "(?=.*extent)(?=.*decision)(?=.*participate)(?=.*motivated)|(?=.*please)(?=.*choose)(?=.*position)(?=.*following)(?=.*statements)(?=.*came)(?=.*hackathon)"
  },
  {
    "title": "How many hackathons have you participated in the past?",
    "question_type": "single_question",
    "answer_type": "int",
    "values": [],
    "keywords": "(?=.*many)(?=.*hackathons)(?=.*participated)|(?=.*many)(?=.*similar)(?=.*events)(?=.*participate)(?=.*past)"
  },
  {
    "title": "How many people were in your team (including yourself)?",
    "question_type": "single_question",
    "answer_type": "int",
    "values": [],
    "keywords": "(?=.*many)(?=.*people)(?=.*team)|(?=.*many)(?=.*members)(?=.*team)"
  },
  {
    "title": "Was there a team leader?",
    "question_type": "category_question",
    "answer_type": "string",
    "values": [],
    "answers": [
      "Yes, I was the team leader.",
      "Yes, someone else was the team leader.",
      "No, there was no clear leader in the team."
    ],
    "keywords": "(?=.*team)(?=.*leader)|(?=.*group)(?=.*leader)"
  },
  {
    "title": "Was there a project manager?",
    "question_type": "category_question",
    "answer_type": "string",
    "values": [],
    "answers": [
      "Yes, I was the project manager.",
      "Yes, someone else was the project manager.",
      "No, there was no clear project manager in the team."
    ],
    "keywords": "(?=.*project)(?=.*manager)"
  },
  {
    "title": "Was there a social-emotional leader?",
    "question_type": "category_question",
    "answer_type": "string",
    "values": [],
    "answers": [
      "Yes, I was the social-emotional leader.",
      "Yes, someone else was the social-emotional leader.",
      "No, there was no clear social-emotional in the team."
    ],
    "keywords": "(?=.*social-emotional)(?=.*leader)"
  },
  {
    "title": "How well did you know your team members?",
    "question_type": "score_question",
    "answer_type": "string_to_int",
    "sub_questions": [
      {
        "title": "I knew my team members well.",
        "values": [],
        "keywords": "(?=.*knew)(?=.*team)(?=.*members)(?=.*well)"
      },
      {
        "title": "I have collaborated with some of my team members before.",
        "values": [],
        "keywords": "(?=.*collaborated)(?=.*team)(?=.*members)"
      },
      {
        "title": "I have been close to some of my team members before.",
        "values": [],
        "keywords": "(?=.*close)(?=.*team)(?=.*members)"
      },
      {
        "title": "I have socialized with some of my team members (outside of this hackathon) before.",
        "values": [],
        "keywords": "(?=.*socialized)(?=.*team)(?=.*members)(?=.*outside)(?=.*hackathon)|(?=.*socialized)(?=.*team)(?=.*members)(?=.*outside)(?=.*work)"
      }
    ],
    "answers": {
      "Strongly disagree": 1,
      "Somewhat disagree": 2,
      "Neither agree nor disagree": 3,
      "Somewhat agree": 4,
      "Strongly agree": 5
    },
    "keywords": "(?=.*well)(?=.*know)(?=.*team)(?=.*members)"
  },
  {
    "title": "Would you describe your team process as more...",
    "question_type": "score_question",
    "answer_type": "int",
    "sub_questions": [
      {
        "title": "(1) Inefficient to (5) Efficient",
        "values": [],
        "keywords": "(?=.*inefficient)(?=.*efficient)"
      },
      {
        "title": "(1) Uncoordinated to (5) Coordinated",
        "values": [],
        "keywords": "(?=.*uncoordinated)(?=.*coordinated)"
      },
      {
        "title": "(1) Unfair to (5) Fair",
        "values": [],
        "keywords": "(?=.*unfair)(?=.*fair)"
      },
      {
        "title": "(1) Confusing to (5) Easy to understand",
        "values": [],
        "keywords": "(?=.*confusing)(?=.*easy)(?=.*understand)"
      }
    ],
    "keywords": "(?=.*would)(?=.*describe)(?=.*team)(?=.*process)|(?=.*would)(?=.*describe)(?=.*group's)(?=.*work)(?=.*process)"
  },
  {
    "title": "Please indicate your level of agreement with the following statements related to your GOALS as a team.",
    "question_type": "score_question",
    "answer_type": "string_to_int",
    "sub_questions": [
      {
        "title": "I was uncertain of my duties and responsibilities in this team.",
        "values": [],
        "keywords": "(?=.*uncertain)(?=.*duties)(?=.*responsibilities)(?=.*team)"
      },
      {
        "title": "I was unclear about the goals and objectives for my work in this team.",
        "values": [],
        "keywords": "(?=.*unclear)(?=.*goals)(?=.*objectives)(?=.*work)(?=.*team)"
      },
      {
        "title": "I was unsure how my work relates to the overall objectives of my team.",
        "values": [],
        "keywords": "(?=.*unsure)(?=.*work)(?=.*relates)(?=.*overall)(?=.*objectives)(?=.*team)"
      }
    ],
    "answers": {
      "Strongly disagree": 1,
      "Somewhat disagree": 2,
      "Neither agree nor disagree": 3,
      "Somewhat agree": 4,
      "Strongly agree": 5
    },
    "keywords": "(?=.*agree)(?=.*following)(?=.*statements)(?=.*related)(?=.*goals)(?=.*team)|(?=.*extent)(?=.*agree)(?=.*following)(?=.*statements)(?=.*related)(?=.*group)(?=.*previously)(?=.*identified)"
  },
  {
    "title": "Please indicate your level of agreement with the following statements about your TEAM.",
    "question_type": "score_question",
    "answer_type": "string_to_int",
    "sub_questions": [
      {
        "title": "Everyone had a chance to express his/her opinion.",
        "values": [],
        "keywords": "(?=.*everyone)(?=.*chance)(?=.*express)(?=.*opinion)"
      },
      {
        "title": "The team members responded to the comments made by others.",
        "values": [],
        "keywords": "(?=.*team)(?=.*members)(?=.*responded)(?=.*comments)(?=.*made)(?=.*others)"
      },
      {
        "title": "The team members participated very actively during the project.",
        "values": [],
        "keywords": "(?=.*members)(?=.*participated)(?=.*actively)"
      },
      {
        "title": "Overall, the participation of each member in the team was effective.",
        "values": [],
        "keywords": "(?=.*overall)(?=.*participation)(?=.*member)(?=.*team)(?=.*effective)"
      }
    ],
    "answers": {
      "Strongly disagree": 1,
      "Somewhat disagree": 2,
      "Neither agree nor disagree": 3,
      "Somewhat agree": 4,
      "Strongly agree": 5
    },
    "keywords": "(?=.*indicate)(?=.*level)(?=.*agreement)(?=.*following)(?=.*statements)(?=.*team)(?!.*goals)|(?=.*extent)(?=.*agree)(?=.*following)(?=.*statements)(?=.*team's)(?=.*work)(?!.*goals)|(?=.*extent)(?=.*agree)(?=.*following)(?=.*statements)(?=.*related)(?=.*communication)(?=.*within)(?=.*team)|(?=.*extent)(?=.*agree)(?=.*following)(?=.*statements)(?=.*group's)(?=.*work)"
  },
  {
    "title": "Please indicate your level of agreement with the following statements related to your SATISFACTION with your project.",
    "question_type": "score_question",
    "answer_type": "string_to_int",
    "sub_questions": [
      {
        "title": "I am satisfied with the work completed in my project.",
        "values": [],
        "keywords": "(?=.*satisfied)(?=.*work)(?=.*completed)(?=.*project)"
      },
      {
        "title": "I am satisfied with the quality of my team's output.",
        "values": [],
        "keywords": "(?=.*satisfied)(?=.*quality)(?=.*teams)(?=.*output)"
      },
      {
        "title": "My ideal outcome coming into my project achieved.",
        "values": [],
        "keywords": "(?=.*ideal)(?=.*outcome)(?=.*coming)(?=.*project)(?=.*achieved)"
      },
      {
        "title": "My expectations towards my team were met.",
        "values": [],
        "keywords": "(?=.*expectations)(?=.*towards)(?=.*team)(?=.*met)|(?=.*expectations)(?=.*towards)(?=.*project)(?=.*met)"
      }
    ],
    "answers": {
      "Strongly disagree": 1,
      "Somewhat disagree": 2,
      "Neither agree nor disagree": 3,
      "Somewhat agree": 4,
      "Strongly agree": 5
    },
    "keywords": "(?=.*indicate)(?=.*level)(?=.*agreement)(?=.*following)(?=.*statements)(?=.*related)(?=.*satisfaction)(?=.*project)|(?=.*extent)(?=.*agree)(?=.*following)(?=.*statements)(?=.*team's)(?=.*project)|(?=.*extend)(?=.*agree)(?=.*following)(?=.*statements)(?=.*team's)(?=.*project)"
  },
  {
    "title": "Please indicate your level of agreement with the following statements related to the USEFULNESS of your project.",
    "question_type": "score_question",
    "answer_type": "string_to_int",
    "sub_questions": [
      {
        "title": "My project improves my performance during my everyday work.",
        "values": [],
        "keywords": "(?=.*project)(?=.*improves)(?=.*performance)(?=.*everyday)(?=.*work)"
      },
      {
        "title": "My project improves my productivity during my everyday work.",
        "values": [],
        "keywords": "(?=.*project)(?=.*improves)(?=.*productivity)(?=.*everyday)(?=.*work)"
      },
      {
        "title": "My project improves my effectiveness during my everyday work.",
        "values": [],
        "keywords": "(?=.*project)(?=.*improves)(?=.*effectiveness)(?=.*everyday)(?=.*work)"
      },
      {
        "title": "Overall, my project will be useful during my everyday work.",
        "values": [],
        "keywords": "(?=.*overall)(?=.*project)(?=.*useful)(?=.*everyday)(?=.*work)"
      }
    ],
    "answers": {
      "Strongly disagree": 1,
      "Somewhat disagree": 2,
      "Neither agree nor disagree": 3,
      "Somewhat agree": 4,
      "Strongly agree": 5
    },
    "keywords": "(?=.*indicate)(?=.*level)(?=.*agreement)(?=.*following)(?=.*statements)(?=.*related)(?=.*usefulness)(?=.*project)"
  },
  {
    "title": "Please indicate your FUTURE INTENTIONS related to your hackathon project.",
    "question_type": "score_question",
    "answer_type": "string_to_int",
    "sub_questions": [
      {
        "title": "I intend to continue working on my hackathon project rather than not continue working on it.",
        "values": [],
        "keywords": "(?=.*intend)(?=.*continue)(?=.*working)(?=.*hackathon)(?=.*project)(?=.*rather)(?=.*not)(?=.*continue)(?=.*working)"
      },
      {
        "title": "My intentions are to continue working on my hackathon project rather than any other project.",
        "values": [],
        "keywords": "(?=.*intentions)(?=.*continue)(?=.*working)(?=.*hackathon)(?=.*project)(?=.*rather)(?=.*other)(?=.*project)"
      },
      {
        "title": "If I could, I would like to continue working on my hackathon project as much as possible.",
        "values": [],
        "keywords": "(?=.*could)(?=.*would)(?=.*like)(?=.*continue)(?=.*working)(?=.*hackathon)(?=.*project)(?=.*much)(?=.*possible)"
      }
    ],
    "answers": {
      "Strongly disagree": 1,
      "Somewhat disagree": 2,
      "Neither agree nor disagree": 3,
      "Somewhat agree": 4,
      "Strongly agree": 5
    },
    "keywords": "(?=.*indicate)(?=.*future)(?=.*intentions)(?=.*related)(?=.*hackathon)(?=.*project)|(?=.*continuing)(?=.*work)(?=.*project)(?=.*future)|(?=.*please)(?=.*indicate)(?=.*level)(?=.*agreement)(?=.*following)(?=.*statements)(?=.*related)(?=.*practices)(?=.*tools)(?=.*identified)"
  },
  {
    "title": "Please indicate your level of agreement with the following statements related to your ABILITY to continue working on your hackathon project.",
    "question_type": "score_question",
    "answer_type": "string_to_int",
    "sub_questions": [
      {
        "title": "I would be able to continue working on my hackathon project.",
        "values": [],
        "keywords": "(?=.*would)(?=.*able)(?=.*continue)(?=.*working)(?=.*hackathon)(?=.*project)"
      },
      {
        "title": "Continuing to work on my hackathon project is entirely under my control.",
        "values": [],
        "keywords": "(?=.*continuing)(?=.*work)(?=.*hackathon)(?=.*project)(?=.*entirely)(?=.*control)"
      },
      {
        "title": "I have the resources, knowledge, and ability to continue working on my project after the hackathon.",
        "values": [],
        "keywords": "(?=.*resources)(?=.*knowledge)(?=.*ability)(?=.*continue)(?=.*working)(?=.*project)(?=.*hackathon)"
      }
    ],
    "answers": {
      "Strongly disagree": 1,
      "Somewhat disagree": 2,
      "Neither agree nor disagree": 3,
      "Somewhat agree": 4,
      "Strongly agree": 5
    },
    "keywords": "(?=.*indicate)(?=.*level)(?=.*agreement)(?=.*following)(?=.*statements)(?=.*related)(?=.*ability)(?=.*continue)(?=.*working)(?=.*hackathon)(?=.*project)"
  },
  {
    "title": "To what extent do you agree with the following statements about THE SUPPORT THE MENTORS PROVIDED during this hackathon?",
    "question_type": "group_question",
    "answer_type": "string_to_int",
    "sub_questions": [
      {
        "title": "The mentors supported us to scope our project.",
        "values": [],
        "keywords": "(?=.*mentors)(?=.*supported)(?=.*us)(?=.*scope)(?=.*project)"
      },
      {
        "title": "The mentors took decisions about the direction of our project.",
        "values": [],
        "keywords": "(?=.*mentors)(?=.*took)(?=.*decisions)(?=.*direction)(?=.*project)"
      },
      {
        "title": "The mentors provided us with solutions to technical problems we encountered.",
        "values": [],
        "keywords": "(?=.*mentors)(?=.*provided)(?=.*us)(?=.*solutions)(?=.*technical)(?=.*problems)(?=.*encountered)"
      },
      {
        "title": "The mentors helped us to find our own solutions to technical problems we encountered.",
        "values": [],
        "keywords": "(?=.*mentors)(?=.*helped)(?=.*us)(?=.*find)(?=.*solutions)(?=.*technical)(?=.*problems)(?=.*encountered)"
      },
      {
        "title": "The mentor were mainly focused on our learning progress.",
        "values": [],
        "keywords": "(?=.*mentor)(?=.*mainly)(?=.*focused)(?=.*learning)"
      },
      {
        "title": "The mentors were mainly focused on our project progress.",
        "values": [],
        "keywords": "(?=.*mentors)(?=.*mainly)(?=.*focused)(?=.*project)(?=.*progress)"
      },
      {
        "title": "The mentors were part of our team.",
        "values": [],
        "keywords": "(?=.*mentor)(?=.*part)(?=.*team)"
      },
      {
        "title": "The mentors showed interest in us beyond the project we were working on.",
        "values": [],
        "keywords": "(?=.*mentors)(?=.*showed)(?=.*interest)(?=.*us)(?=.*beyond)(?=.*project)(?=.*working)"
      },
      {
        "title": "We could reach the mentors when we needed help.",
        "values": [],
        "keywords": "(?=.*could)(?=.*reach)(?=.*mentors)(?=.*needed)(?=.*help)"
      }
    ],
    "answers": {
      "Strongly disagree": 1,
      "Somewhat disagree": 2,
      "Neither agree nor disagree": 3,
      "Somewhat agree": 4,
      "Strongly agree": 5
    },
    "keywords": "(?=.*extent)(?=.*agree)(?=.*following)(?=.*statements)(?=.*support)(?=.*mentor)(?=.*provided)"
  },
  {
    "title": "How do you feel about your OVERALL EXPERIENCE participating in this hackathon?",
    "question_type": "score_question",
    "answer_type": "int",
    "sub_questions": [
      {
        "title": "(1) Very dissatisfied to (5) Very satisfied",
        "values": [],
        "keywords": "(?=.*dissatisfied)(?=.*satisfied)"
      },
      {
        "title": "(1) Very displeased to (5) Very pleased",
        "values": [],
        "keywords": "(?=.*displeased)(?=.*pleased)"
      },
      {
        "title": "(1) Very frustrated to (5) Very contented",
        "values": [],
        "keywords": "(?=.*frustrated)(?=.*contented)"
      },
      {
        "title": "(1) Absolutely terrible to (5) Absolutely delighted",
        "values": [],
        "keywords": "(?=.*absolutely)(?=.*terrible)(?=.*absolutely)(?=.*delighted)"
      }
    ],
    "keywords": "(?=.*feel)(?=.*overall)(?=.*experience)(?=.*participating)(?=.*hackathon)|(?=.*feel)(?=.*outcome)(?=.*hackathon)(?=.*project)"
  },
  {
    "title": "Do people identify with the community?",
    "question_type": "score_question",
    "answer_type": "string_to_int",
    "sub_questions": [
      {
        "title": "I identify with other members of this community.",
        "values": [],
        "keywords": "(?=.*identify)(?=.*members)(?=.*community)"
      },
      {
        "title": "I am like other members of this community.",
        "values": [],
        "keywords": "(?=.*like)(?=.*members)(?=.*community)"
      },
      {
        "title": "This community is an important reflection of who I am.",
        "values": [],
        "keywords": "(?=.*community)(?=.*important)(?=.*reflection)"
      },
      {
        "title": "I would like to continue working with this community.",
        "values": [],
        "keywords": "(?=.*would)(?=.*like)(?=.*continue)(?=.*working)(?=.*community)"
      },
      {
        "title": "I dislike being a member of this community",
        "values": [],
        "keywords": "(?=.*dislike)(?=.*member)(?=.*community)"
      },
      {
        "title": "I would rather belong to another community.",
        "values": [],
        "keywords": "(?=.*would)(?=.*rather)(?=.*belong)(?=.*another)(?=.*community)"
      }
    ],
    "answers": {
      "Strongly disagree": 1,
      "Somewhat disagree": 2,
      "Neither agree nor disagree": 3,
      "Somewhat agree": 4,
      "Strongly agree": 5
    },
    "keywords": "(?=.*people)(?=.*identify)(?=.*community)"
  },
  {
    "title": "To what extent do you agree with the following statements about your relationship with the community?",
    "question_type": "score_question",
    "answer_type": "string_to_int",
    "sub_questions": [
      {
        "title": "I feel I am part of this community.",
        "values": [],
        "keywords": "(?=.*feel)(?=.*i)(?=.*am)(?=.*part)(?=.*community)"
      },
      {
        "title": "I am interested in what goes on in this community.",
        "values": [],
        "keywords": "(?=.*interested)(?=.*goes)(?=.*community)"
      },
      {
        "title": "Interacting with other members of this community makes me want to try new things.",
        "values": [],
        "keywords": "(?=.*interacting)(?=.*community)(?=.*makes)(?=.*want)(?=.*try)(?=.*new)(?=.*things)"
      },
      {
        "title": "I am willing to spend time to support general activities in this community.",
        "values": [],
        "keywords": "(?=.*willing)(?=.*spend)(?=.*time)(?=.*support)(?=.*general)(?=.*activities)(?=.*community)"
      },
      {
        "title": "Through this community I come into contact with new people all the time.",
        "values": [],
        "keywords": "(?=.*community)(?=.*come)(?=.*contact)(?=.*new)(?=.*people)(?=.*time)"
      },
      {
        "title": "There are several people in this community that I trust to help me solve my problems.",
        "values": [],
        "keywords": "(?=.*several)(?=.*community)(?=.*trust)(?=.*help)(?=.*solve)(?=.*problems)"
      },
      {
        "title": "I know someone in this community that I can turn to if I urgently need help.",
        "values": [],
        "keywords": "(?=.*know)(?=.*someone)(?=.*community)(?=.*turn)(?=.*urgently)(?=.*need)(?=.*help)"
      },
      {
        "title": "There is someone in this community that I can turn to for advice about making important decision.",
        "values": [],
        "keywords": "(?=.*someone)(?=.*community)(?=.*turn)(?=.*advice)(?=.*making)(?=.*important)(?=.*decision)"
      },
      {
        "title": "The other members of this community would be good job references for me.",
        "values": [],
        "keywords": "(?=.*would)(?=.*good)(?=.*job)(?=.*references)"
      },
      {
        "title": "I do not know people in this community well enough to get them to do anything important.",
        "values": [],
        "keywords": "(?=.*know)(?=.*people)(?=.*community)(?=.*well)(?=.*enough)(?=.*get)(?=.*anything)(?=.*important)"
      }
    ],
    "keywords": "(?=.*extent)(?=.*agree)(?=.*following)(?=.*statements)(?=.*relationship)(?=.*community)|(?=.*experience)(?=.*part)(?=.*community)(?=.*around)(?=.*hackathon)"
  },
  {
    "title": "Do you plan to participate in a similar event in the future?",
    "question_type": "single_question",
    "answer_type": "string_to_int",
    "values": [],
    "answers": {
      "Definitely not": 1,
      "Probably not": 2,
      "Might of might not": 3,
      "Probably yes": 4,
      "Definitely yes": 5
    },
    "keywords": "(?=.*plan)(?=.*participate)(?=.*similar)(?=.*event)(?=.*future)"
  },
  {
    "title": "How likely would you recommend a similar hackathon to a friend or colleague?",
    "question_type": "single_question",
    "answer_type": "int",
    "values": [],
    "keywords": "(?=.*likely)(?=.*would)(?=.*recommend)(?=.*similar)(?=.*hackathon)(?=.*friend)(?=.*colleague)"
  },
  {
    "title": "How many years of programming experience do you have?",
    "question_type": "single_question",
    "answer_type": "int",
    "values": [],
    "keywords": "(?=.*many)(?=.*years)(?=.*programming)(?=.*experience)"
  },
  {
    "title": "Referring back to the people you collaborated with at this hackathon, how do you estimate your programming experience compared to them?",
    "question_type": "single_question",
    "answer_type": "string_to_int",
    "values": [],
    "answers": {
      "Very inexperienced": 1,
      "Inexperienced": 2,
      "Comparable": 3,
      "Experienced": 4,
      "Very experienced": 5
    },
    "keywords": "(?=.*referring)(?=.*back)(?=.*people)(?=.*collaborated)(?=.*hackathon)(?=.*estimate)(?=.*programming)(?=.*experience)(?=.*compared)"
  },
  {
    "title": "How old are you currently?",
    "question_type": "category_question",
    "answer_type": "string",
    "values": [],
    "answers": [
      "18 to 24",
      "25 to 34",
      "35 to 44",
      "45 to 54",
      "55 to 64",
      "65 to 74",
      "75 or older",
      "Prefer not to say"
    ],
    "keywords": "(?=.*old)(?=.*currently)|(?=.*your)(?=.*age)"
  },
  {
    "title": "Are you...?",
    "question_type": "category_question",
    "answer_type": "string",
    "values": [],
    "answers": [
      "Female",
      "Male",
      "Non-binary",
      "Prefer not to say"
    ],
    "keywords": "(?=.*are)(?=.*you\.\.\.\?)|(?=.*following)(?=.*accurately)(?=.*describe)(?=.*you)|(?=.*gender)^((?!minority).)*$"
  },
  {
    "title": "What is highest level of formal education that you have completed until now?",
    "question_type": "category_question",
    "answer_type": "string",
    "values": [],
    "answers": [
      "High school diploma or GED",
      "Some college",
      "Associate and/or bachelor's degree",
      "Bachelor's degree",
      "Professional degree",
      "Master's degree",
      "Doctorate",
      "Prefer not to say"
    ],
    "keywords": "(?=.*highest)(?=.*level)(?=.*formal)(?=.*education)(?=.*completed)"
  },
  {
    "title": "Do you consider yourself a minority? (For example in terms of race, gender, expertise or in another way)",
    "question_type": "category_question",
    "answer_type": "string",
    "values": [],
    "answers": [
      "Yes",
      "No",
      "Prefer not to say"
    ],
    "keywords": "(?=.*consider)(?=.*yourself)(?=.*minority)"
  }
]

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
        #If not matches are found with keywords, use fuzzy matching
        matches = find_matches_fuzzy(title)
        if len(matches) == 0:
            regex = generate_keywords_regex(title)
            print(f'Created regex for question "{title}": {regex}')
        elif len(matches) > 1:
            print(f'Question "{title}" of hackathon "{hackathon}" matched multiple questions with fuzzy matching: {"; ".join(matches)}')
    elif len(matches) > 1:
        print(f'Question "{title}" of hackathon "{hackathon}" matched multiple questions with keywords: {"; ".join(matches)}')

def generate_keywords_regex(title: str) -> str:
    '''Generate a regex, that matches for all words of a title, with stopwords removed'''
    #Turn lowercase
    title = title.lower()
    #Create array of words
    words = title.split(' ')
    #Remove characters that are not alphanumeric
    for i in range(len(words)):
        words[i] = ''.join(char for char in words[i] if char.isalpha())
    #Remove stopwords
    words = [word for word in words if word not in STOP_WORDS]
    #Return regex that checks for all words
    return ''.join(f'(?=.*{word})' for word in words)

def generate_keywords_for_all_hackathons():
    '''Iterate over all hackathons in the defined folder'''
    overview = pd.read_excel(f'{FOLDER_PATH}/!hackathons-overview.xlsx')
    for i, found_hackathon in overview.iterrows():
        generate_keywords_for_single_hackathon(found_hackathon['ID'])

def generate_keywords_for_single_hackathon(hackathon_id: str):
    '''Generate keyword regexes for all questions of a hackathon, that are not identified by the existing keywords or fuzzy string matching of the titles'''
    print(f'-----------------------------Hackathon ID: {hackathon_id}----------------------------------')
    file = pd.read_csv(f'{FOLDER_PATH}/{hackathon_id}.csv')
    for title in file.keys():
        #If the title contains square brackets, this is a subquestion
        if '[' in title:
            title_sections = title.split('[')
            question_title = title_sections[0]
            
            #Handle question title
            find_matches(hackathon_id, question_title)

            #Handle subquestion title
            subquestion_title = title_sections[1].split(']')[0]
            find_matches(hackathon_id, subquestion_title)
        #If not, this is a single question
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