from models.HackathonInformation import HackathonInformation
from enum import Enum
from pydantic import BaseModel

class Minority(Enum):
    YES = 'yes'
    NO = 'no'
    PREFER_NOT_TO_SAY = 'prefer-not-to-say'

class Education(Enum):
    HIGH_SCHOOL = 'high-school'
    COLLEGE = 'college'
    ASSOCIATE = 'associate'
    BACHELOR = 'bachelor'
    PROFESSIONAL = 'professional'
    MASTER = 'master'
    DOCTOR = 'doctor'
    PREFER_NOT_TO_SAY = 'prefer-not-to-say'

class Gender(Enum):
    FEMALE = 'female'
    MALE = 'male'
    NON_BINARY = 'non-binary'
    PREFER_NOT_TO_SAY = 'prefer-not-to-say'

class Age(Enum):
    EIGHTEEN = '18'
    TWENTYFIVE = '25'
    THIRTYFIVE = '35'
    FOURTYFIVE = '45'
    FIFTYFIVE = '55'
    SIXTYFIVE = '65'
    SEVENTYFIVE = '75'
    PREFER_NOT_TO_SAY = 'prefer-not-to-say'

class ProgrammingMeasure(BaseModel):
    java: list[int] | None = None
    javascript: list[int] | None = None
    python: list[int] | None = None
    html: list[int] | None = None
    django: list[int] | None = None
    requests: list[int] | None = None
    jupyter_notebooks: list[int] | None = None

class SessionMeasure(BaseModel):
    pre_event_webinar: list[int] | None = None
    checkpoints: list[int] | None = None
    mentoring_sessions: list[int] | None = None

class MentoringExperience(BaseModel):
    scope: list[int] | None = None
    direction: list[int] | None = None
    technical_problems_solutions_provided: list[int] | None = None
    technical_problems_solutions_helped: list[int] | None = None
    learning_progress: list[int] | None = None
    project_progress: list[int] | None = None
    part_of_team: list[int] | None = None
    interest: list[int] | None = None
    reach: list[int] | None = None

class LeaderMeasure(Enum):
    YES = 'yes'
    YES_OTHER = 'yes-other'
    NO = 'no'

class Motivation(BaseModel):
    having_fun: list[int] | None = None
    making_something_cool: list[int] | None = None
    learning_new_tools: list[int] | None = None
    meeting_new_people: list[int] | None = None
    seeing_what_others_are_working_on: list[int] | None = None
    sharing_my_experience: list[int] | None = None
    joining_friends: list[int] | None = None
    dedicated_time: list[int] | None = None
    win_a_prize: list[int] | None = None

class Measures(BaseModel):
    motivation: Motivation = Motivation()
    event_participation: list[int] | None = None
    team_size: list[int] | None = None
    team_leader: list[LeaderMeasure] | None = None
    team_manager: list[LeaderMeasure] | None = None
    social_leader: list[LeaderMeasure] | None = None
    team_familiarity: list[int] | None = None
    satisfaction_with_process: list[int] | None = None
    goal_clarity: list[int] | None = None
    voice: list[int] | None = None
    satisfaction_with_outcome: list[int] | None = None
    perceived_usefulness: list[int] | None = None
    continuation_intentions: list[int] | None = None
    behavioral_control: list[int] | None = None
    mentoring_experience: MentoringExperience = MentoringExperience()
    community_identification: list[int] | None = None
    social_capital: list[int] | None = None
    satisfaction_with_hackathon: list[int] | None = None
    future_participation_intentions: list[int] | None = None
    recommendation_likeliness: list[int] | None = None
    session_satisfaction: SessionMeasure = SessionMeasure()
    session_usefulness: SessionMeasure = SessionMeasure()
    session_enjoyment: SessionMeasure = SessionMeasure()
    programming_experience_years: list[int] | None = None
    programming_experience_comparison: list[int] | None = None
    programming_ability: ProgrammingMeasure = ProgrammingMeasure()
    programming_comfort: ProgrammingMeasure = ProgrammingMeasure()
    age: list[Age] | None = None
    gender: list[Gender] | None = None
    education: list[Education] | None = None
    minority: list[Minority] | None = None

class Hackathon(HackathonInformation):
    results: Measures