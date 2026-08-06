from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# --- STEP 1: JOB INTAKE & PLANNING MODELS ---
class JobIntakePlan(BaseModel):
    role_title: str = Field(description="Title of the open position")
    department: str = Field(description="Department or team name")
    key_skills_needed: List[str] = Field(description="Primary core skills required")
    generated_job_description: str = Field(description="AI-generated full professional Job Description")
    min_salary_band: str = Field(description="Minimum salary e.g. 18 LPA or $120k")
    max_salary_band: str = Field(description="Maximum salary e.g. 28 LPA or $170k")
    currency: str = Field(default="INR", description="Currency e.g. INR or USD")

# --- STEP 2: SOURCING & SCREENING MODELS ---
class ShortlistEmail(BaseModel):
    candidate_name: str
    candidate_email: str
    role_title: str
    email_subject: str
    email_body: str
    sent_timestamp: str

class CategoryScore(BaseModel):
    category: str = Field(description="Category name e.g. Technical Skills, Experience, Education, Work Mode & Location Fit")
    score: int = Field(description="Score out of 100", ge=0, le=100)
    strengths: List[str] = Field(description="Identified candidate strengths")
    gaps: List[str] = Field(description="Identified gaps or missing qualifications")
    summary: str = Field(description="Brief commentary explaining the score")

class CandidateScreening(BaseModel):
    candidate_name: str = Field(description="Candidate name")
    candidate_email: str = Field(default="candidate@example.com")
    overall_match_score: int = Field(description="Overall match score out of 100", ge=0, le=100)
    recommendation: Literal["STRONG_PASS", "INTERVIEW", "HOLD", "REJECT"] = Field(description="Recommendation")
    executive_summary: str = Field(description="3-4 sentence summary of candidate suitability")
    experience_fit_commentary: str = Field(description="Assessment of total experience vs required experience")
    work_mode_and_location_fit: str = Field(description="Assessment of location and work mode (Remote/Office/Hybrid)")
    salary_expectation_fit: str = Field(default="Fits target salary band")
    key_qualifications: List[str] = Field(description="Primary highlights matching JD")
    critical_gaps: List[str] = Field(description="Main dealbreakers or missing requirements")
    category_scores: List[CategoryScore] = Field(description="Breakdown across key dimensions")

class EvaluationCritique(BaseModel):
    quality_score: int = Field(description="QA audit score out of 100", ge=0, le=100)
    needs_revision: bool = Field(description="True if screening report needs deeper refinement")
    critique_notes: List[str] = Field(description="Specific feedback on missing details or errors")
    focus_areas_for_refinement: List[str] = Field(description="Refinement focus areas")

# --- STEP 3: INTERVIEW, SELECTION, OFFER & ONBOARDING MODELS ---
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

class TelephonicScreeningResult(BaseModel):
    candidate_name: str
    interest_level: str = Field(description="High / Medium / Low")
    availability_and_notice_period: str = Field(description="Immediate / 30 Days / 60 Days / 90 Days")
    salary_expectation: str = Field(description="Candidate expected compensation")
    communication_rating: int = Field(description="Score out of 10 for communication", ge=0, le=10)
    culture_fit_notes: str = Field(description="Notes on team culture alignment")
    preliminary_status: Literal["PASSED", "HOLD", "REJECTED"] = Field(description="Status of telephonic round")

class HITLDecision(BaseModel):
    checkpoint_name: str = Field(description="Name of HITL checkpoint e.g. Manager Interview Approval or Final Offer Approval")
    approved_by_manager: bool = Field(description="True if human manager approves, False if rejected")
    manager_notes: str = Field(description="Human manager comments, special instructions, or custom salary ceiling")
    decision_timestamp: str

class OfferLetter(BaseModel):
    candidate_name: str
    role_title: str
    offered_ctc: str = Field(description="Agreed annual salary package e.g. 24 LPA")
    joining_bonus: Optional[str] = Field(default="None")
    work_mode: str = Field(description="Remote / Work From Office / Hybrid")
    office_location: str
    date_of_joining: str = Field(description="Expected Joining Date e.g. 1st September 2026")
    offer_letter_text: str = Field(description="Full text of the formal offer letter")

class BGVReport(BaseModel):
    candidate_name: str
    employment_verification: Literal["CLEAR", "NEEDS_REVIEW", "FAILED"]
    education_verification: Literal["CLEAR", "NEEDS_REVIEW", "FAILED"]
    identity_and_address_check: Literal["CLEAR", "NEEDS_REVIEW", "FAILED"]
    overall_bgv_status: Literal["PASSED", "CONDITIONAL_PASS", "FAILED"]
    bgv_summary_notes: str

class OnboardingPackage(BaseModel):
    candidate_name: str
    role_title: str
    start_date: str
    paperwork_checklist: List[str] = Field(description="List of required onboarding documents")
    it_equipment_allocation: List[str] = Field(description="Assigned hardware (Laptop, Security Keys, Monitor)")
    first_week_orientation_schedule: List[str] = Field(description="Day-by-day orientation plan")

# --- AGENT STATE DICTIONARY ---
class AgentState(TypedDict):
    # Step 1
    job_intake_plan: Optional[Dict[str, Any]]
    job_description: str
    required_experience: str
    work_mode: str
    target_location: str
    salary_band_min: str
    salary_band_max: str
    
    # Step 2
    candidate_resume: str
    job_postings_status: Optional[List[str]]
    screening_report: Optional[Dict[str, Any]]
    critique: Optional[Dict[str, Any]]
    shortlist_email: Optional[Dict[str, Any]]
    reflection_count: int
    
    # Step 3
    telephonic_result: Optional[Dict[str, Any]]
    hitl_checkpoint1_manager_approval: Optional[Dict[str, Any]]
    salary_negotiation_details: Optional[Dict[str, Any]]
    hitl_checkpoint2_offer_approval: Optional[Dict[str, Any]]
    official_offer_letter: Optional[Dict[str, Any]]
    bgv_report: Optional[Dict[str, Any]]
    onboarding_package: Optional[Dict[str, Any]]
    
    # Logs & Execution Flags
    execution_logs: List[Dict[str, Any]]
    current_step: int
    is_complete: bool
