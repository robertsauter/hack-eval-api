from models.HackathonInformation import HackathonInformation
from pydantic import BaseModel
from typing import Literal

Minority = Literal['yes', 'no', 'prefer-not-to-say']

Education = Literal['high-school', 'college', 'associate', 'bachelor', 'professional', 'master', 'doctor', 'prefer-not-to-say']

Gender = Literal['female', 'male', 'non-binary', 'prefer-not-to-say']

Age = Literal['18', '25', '35', '45', '55', '65', '75', 'prefer-not-to-say']

LeaderMeasure = Literal['yes', 'yes-other', 'no']

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