from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

class CategoryScore(BaseModel):
    category: str = Field(description="Category name, e.g. Technical Skills, Experience, Education, Culture Fit")
    score: int = Field(description="Score out of 100", ge=0, le=100)
    strengths: List[str] = Field(description="Identified candidate strengths in this category")
    gaps: List[str] = Field(description="Identified gaps or missing qualifications")
    summary: str = Field(description="Brief commentary explaining the score")

class CandidateScreening(BaseModel):
    candidate_name: str = Field(description="Name of the candidate extracted from resume")
    overall_match_score: int = Field(description="Overall match percentage out of 100", ge=0, le=100)
    recommendation: Literal["STRONG_PASS", "INTERVIEW", "HOLD", "REJECT"] = Field(description="Hiring recommendation")
    executive_summary: str = Field(description="High-level 3-4 sentence summary of candidate suitability")
    key_qualifications: List[str] = Field(description="Primary highlights matching the job description")
    critical_gaps: List[str] = Field(description="Main dealbreakers or missing requirements")
    category_scores: List[CategoryScore] = Field(description="Breakdown across key evaluation dimensions")

class EvaluationCritique(BaseModel):
    quality_score: int = Field(description="QA score out of 100 on the thoroughness and accuracy of the screening", ge=0, le=100)
    needs_revision: bool = Field(description="True if the screening report needs deeper analysis or correction")
    critique_notes: List[str] = Field(description="Specific feedback on missing details, hallucinated facts, or unverified claims")
    focus_areas_for_refinement: List[str] = Field(description="Areas the screener should re-examine")

class InterviewQuestion(BaseModel):
    question_type: Literal["Technical", "Behavioral", "System Design / Practical", "Culture / Values"] = Field(description="Category of question")
    topic: str = Field(description="Specific topic or skill being evaluated")
    question_text: str = Field(description="The exact question to ask during interview")
    why_asked: str = Field(description="Rationale linking to candidate's background or identified gaps")
    ideal_answer_rubric: str = Field(description="Key points to look for in a top candidate response")

class InterviewKit(BaseModel):
    candidate_name: str = Field(description="Name of the candidate")
    suggested_role_level: str = Field(description="Recommended position level e.g. Senior, Mid, Staff")
    interview_focus: str = Field(description="Primary focus areas for interview loop")
    questions: List[InterviewQuestion] = Field(description="List of targeted interview questions")
    overall_hiring_advice: str = Field(description="Final strategic advice for the hiring committee")

class ExecutionStepLog(BaseModel):
    step_name: str
    node_id: str
    detail: str
    timestamp: str

class AgentState(TypedDict):
    job_description: str
    candidate_resume: str
    screening_report: Optional[Dict[str, Any]]
    critique: Optional[Dict[str, Any]]
    interview_kit: Optional[Dict[str, Any]]
    reflection_count: int
    execution_logs: List[Dict[str, Any]]
    is_complete: bool
