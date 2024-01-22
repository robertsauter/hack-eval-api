from models.HackathonInformation import HackathonInformation
from pydantic import BaseModel

class SingleAnalysisMeasure(BaseModel):
    participants: int
    average: float
    deviation: float
    distribution: dict[str, int]

class CategoryAnalysisMeasure(BaseModel):
    participants: int
    distribution: dict[str, int]

class AnalysisProgrammingMeasure(BaseModel):
    java: SingleAnalysisMeasure | None = None
    javascript: SingleAnalysisMeasure | None = None
    python: SingleAnalysisMeasure | None = None
    html: SingleAnalysisMeasure | None = None
    django: SingleAnalysisMeasure | None = None
    requests: SingleAnalysisMeasure | None = None
    jupyter_notebooks: SingleAnalysisMeasure | None = None

class AnalysisSessionMeasure(BaseModel):
    pre_event_webinar: SingleAnalysisMeasure | None = None
    checkpoints: SingleAnalysisMeasure | None = None
    mentoring_sessions: SingleAnalysisMeasure | None = None

class AnalysisMentoringExperience(BaseModel):
    scope: SingleAnalysisMeasure | None = None
    direction: SingleAnalysisMeasure | None = None
    technical_problems_solutions_provided: SingleAnalysisMeasure | None = None
    technical_problems_solutions_helped: SingleAnalysisMeasure | None = None
    learning_progress: SingleAnalysisMeasure | None = None
    project_progress: SingleAnalysisMeasure | None = None
    part_of_team: SingleAnalysisMeasure | None = None
    interest: SingleAnalysisMeasure | None = None
    reach: SingleAnalysisMeasure | None = None

class AnalysisMotivation(BaseModel):
    having_fun: SingleAnalysisMeasure | None = None
    making_something_cool: SingleAnalysisMeasure | None = None
    learning_new_tools: SingleAnalysisMeasure | None = None
    meeting_new_people: SingleAnalysisMeasure | None = None
    seeing_what_others_are_working_on: SingleAnalysisMeasure | None = None
    sharing_my_experience: SingleAnalysisMeasure | None = None
    joining_friends: SingleAnalysisMeasure | None = None
    dedicated_time: SingleAnalysisMeasure | None = None
    win_a_prize: SingleAnalysisMeasure | None = None

class AnalysisMeasures(BaseModel):
    motivation: AnalysisMotivation = AnalysisMotivation()
    event_participation: SingleAnalysisMeasure | None = None
    team_size: SingleAnalysisMeasure | None = None
    team_leader: CategoryAnalysisMeasure | None = None
    team_manager: CategoryAnalysisMeasure | None = None
    social_leader: CategoryAnalysisMeasure | None = None
    team_familiarity: SingleAnalysisMeasure | None = None
    satisfaction_with_process: SingleAnalysisMeasure | None = None
    goal_clarity: SingleAnalysisMeasure | None = None
    voice: SingleAnalysisMeasure | None = None
    satisfaction_with_outcome: SingleAnalysisMeasure | None = None
    perceived_usefulness: SingleAnalysisMeasure | None = None
    continuation_intentions: SingleAnalysisMeasure | None = None
    behavioral_control: SingleAnalysisMeasure | None = None
    mentoring_experience: AnalysisMentoringExperience = AnalysisMentoringExperience()
    community_identification: SingleAnalysisMeasure | None = None
    social_capital: SingleAnalysisMeasure | None = None
    satisfaction_with_hackathon: SingleAnalysisMeasure | None = None
    future_participation_intentions: SingleAnalysisMeasure | None = None
    recommendation_likeliness: SingleAnalysisMeasure | None = None
    session_satisfaction: AnalysisSessionMeasure = AnalysisSessionMeasure()
    session_usefulness: AnalysisSessionMeasure = AnalysisSessionMeasure()
    session_enjoyment: AnalysisSessionMeasure = AnalysisSessionMeasure()
    programming_experience_years: SingleAnalysisMeasure | None = None
    programming_experience_comparison: SingleAnalysisMeasure | None = None
    programming_ability: AnalysisProgrammingMeasure = AnalysisProgrammingMeasure()
    programming_comfort: AnalysisProgrammingMeasure = AnalysisProgrammingMeasure()
    age: CategoryAnalysisMeasure | None = None
    gender: CategoryAnalysisMeasure | None = None
    education: CategoryAnalysisMeasure | None = None
    minority: CategoryAnalysisMeasure | None = None

class Analysis(HackathonInformation):
    results: AnalysisMeasures