import datetime
import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from recruitment_agent.config import config
from recruitment_agent.models import (
    AgentState, JobIntakePlan, CandidateScreening, EvaluationCritique,
    InterviewKit, OfferLetter, HITLDecision
)
from recruitment_agent.llm import generate_structured_output
from recruitment_agent.tools.email_tool import EmailNotificationTool
from recruitment_agent.tools.telephonic_tool import TelephonicScreeningTool
from recruitment_agent.tools.bgv_tool import BackgroundVerificationTool
from recruitment_agent.tools.onboarding_tool import OnboardingTool

logger = logging.getLogger(__name__)

# --- STEP 1 NODES ---
def job_intake_node(state: AgentState) -> Dict[str, Any]:
    """Step 1: Defines job need, generates AI JD, and sets salary bands."""
    title = state.get("job_description", "Senior AI & LangGraph Engineer")
    api_key = state.get("api_key")
    model_name = state.get("model_name")

    system_prompt = (
        "You are an Executive Talent Acquisition Planning Director. "
        "Based on the provided open role title, generate a comprehensive Job Intake Plan including role_title, "
        "department, key_skills_needed, generated_job_description, min_salary_band, and max_salary_band."
    )
    user_prompt = f"Role Title & Need: {title}"

    intake_plan: JobIntakePlan = generate_structured_output(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output_schema=JobIntakePlan,
        api_key=api_key,
        model_name=model_name
    )

    log_entry = {
        "step_name": "Step 1: Job Intake & Planning",
        "node_id": "job_intake_node",
        "detail": f"Generated JD and salary band: {intake_plan.min_salary_band} - {intake_plan.max_salary_band}",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }

    logs = list(state.get("execution_logs", []))
    logs.append(log_entry)

    return {
        "job_intake_plan": intake_plan.model_dump(),
        "job_description": intake_plan.generated_job_description,
        "salary_band_min": intake_plan.min_salary_band,
        "salary_band_max": intake_plan.max_salary_band,
        "execution_logs": logs,
        "current_step": 1
    }

# --- STEP 2 NODES ---
def sourcing_posting_node(state: AgentState) -> Dict[str, Any]:
    """Step 2a-c: Broadcasts job postings and searches active/passive talent."""
    title = state.get("job_description", "")[:50]
    
    postings = [
        "✅ Job posted on LinkedIn Jobs & Recruiter Portal",
        "✅ Job posted on Naukri India Employer Portal",
        "✅ Job posted on Indeed & Foundit (Monster)",
        "✅ Broadcaster sent notification to Internal Referral Network"
    ]

    log_entry = {
        "step_name": "Step 2: Multi-Channel Job Posting",
        "node_id": "sourcing_posting_node",
        "detail": f"Broadcasted job postings across channels for '{title}...'",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }

    logs = list(state.get("execution_logs", []))
    logs.append(log_entry)

    return {
        "job_postings_status": postings,
        "execution_logs": logs
    }

def screener_node(state: AgentState) -> Dict[str, Any]:
    """Step 2d: Rules & Reflection Resume Screening."""
    jd = state.get("job_description", "")
    resume = state.get("candidate_resume", "")
    req_exp = state.get("required_experience", "5-8 Years (Senior)")
    work_mode = state.get("work_mode", "Remote")
    target_loc = state.get("target_location", "San Francisco / Remote")
    sal_min = state.get("salary_band_min", "18 LPA")
    sal_max = state.get("salary_band_max", "28 LPA")
    
    critique = state.get("critique")
    reflection_count = state.get("reflection_count", 0)
    api_key = state.get("api_key")
    model_name = state.get("model_name")

    system_prompt = (
        "You are a Senior Technical Recruiter. Analyze candidate resume against Job Description and rules:\n"
        f"- REQUIRED EXPERIENCE: {req_exp}\n"
        f"- WORK MODE: {work_mode}\n"
        f"- LOCATION: {target_loc}\n"
        f"- SALARY TARGET: {sal_min} - {sal_max}\n\n"
        "Evaluate experience fit, work mode compatibility, location match, technical skills, and critical dealbreaker gaps."
    )
    
    if critique and critique.get("needs_revision"):
        notes = "\n- ".join(critique.get("critique_notes", []))
        system_prompt += f"\n\nREVISION INSTRUCTIONS (Iteration {reflection_count}):\n- {notes}"

    user_prompt = f"JD:\n{jd}\n\nRESUME:\n{resume}"

    screening: CandidateScreening = generate_structured_output(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output_schema=CandidateScreening,
        api_key=api_key,
        model_name=model_name
    )

    log_entry = {
        "step_name": f"Step 2: Resume Screening (Pass {reflection_count + 1})",
        "node_id": "screener_node",
        "detail": f"Screening complete. Score: {screening.overall_match_score}/100, Rec: {screening.recommendation}",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }

    logs = list(state.get("execution_logs", []))
    logs.append(log_entry)

    return {
        "screening_report": screening.model_dump(),
        "execution_logs": logs,
        "current_step": 2
    }

def evaluator_node(state: AgentState) -> Dict[str, Any]:
    """Step 2d QA Audit: Evaluates screening report thoroughness."""
    jd = state.get("job_description", "")
    resume = state.get("candidate_resume", "")
    screening_dict = state.get("screening_report", {})
    reflection_count = state.get("reflection_count", 0)
    api_key = state.get("api_key")
    model_name = state.get("model_name")

    system_prompt = "You are a Director of HR Audit QA. Audit screening report thoroughness, evidence, and accuracy."
    user_prompt = f"JD:\n{jd}\n\nRESUME:\n{resume}\n\nSCREENING REPORT:\n{screening_dict}"

    critique: EvaluationCritique = generate_structured_output(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output_schema=EvaluationCritique,
        api_key=api_key,
        model_name=model_name
    )

    new_count = reflection_count + 1
    log_entry = {
        "step_name": f"Step 2: QA Reflection Audit #{new_count}",
        "node_id": "evaluator_node",
        "detail": f"Audit Score: {critique.quality_score}/100. Needs Revision: {critique.needs_revision}",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }

    logs = list(state.get("execution_logs", []))
    logs.append(log_entry)

    return {
        "critique": critique.model_dump(),
        "reflection_count": new_count,
        "execution_logs": logs
    }

def should_continue_screening(state: AgentState) -> Literal["screener_node", "shortlist_email_node"]:
    """Conditional Edge: Loops back for refinement or proceeds to email notifier."""
    critique = state.get("critique", {})
    reflection_count = state.get("reflection_count", 0)

    if (critique.get("needs_revision", False) or critique.get("quality_score", 100) < config.MIN_PASSING_SCORE) and reflection_count < config.MAX_REFLECTION_LOOPS:
        return "screener_node"
    return "shortlist_email_node"

def shortlist_email_node(state: AgentState) -> Dict[str, Any]:
    """Step 2e: Generates and sends shortlist email notification to candidate."""
    screening = state.get("screening_report", {})
    candidate_name = screening.get("candidate_name", "Candidate")
    candidate_email = screening.get("candidate_email", "candidate@example.com")
    role_title = "Senior AI & LangGraph Engineer"

    email_obj = EmailNotificationTool.send_shortlist_notification(candidate_name, candidate_email, role_title)

    log_entry = {
        "step_name": "Step 2: Shortlist Email Notification",
        "node_id": "shortlist_email_node",
        "detail": f"Sent shortlist email to {candidate_name} ({candidate_email})",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }

    logs = list(state.get("execution_logs", []))
    logs.append(log_entry)

    return {
        "shortlist_email": email_obj.model_dump(),
        "execution_logs": logs
    }

# --- STEP 3 NODES ---
def telephonic_screening_node(state: AgentState) -> Dict[str, Any]:
    """Step 3a: Simulates preliminary telephonic interview round."""
    screening = state.get("screening_report", {})
    candidate_name = screening.get("candidate_name", "Dr. Eleanor Vance")
    
    result = TelephonicScreeningTool.conduct_telephonic_round(candidate_name, "Senior AI Engineer")

    log_entry = {
        "step_name": "Step 3a: Telephonic Preliminary Round",
        "node_id": "telephonic_screening_node",
        "detail": f"Status: {result.preliminary_status}, Availability: {result.availability_and_notice_period}",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }

    logs = list(state.get("execution_logs", []))
    logs.append(log_entry)

    return {
        "telephonic_result": result.model_dump(),
        "execution_logs": logs,
        "current_step": 3
    }

def offer_and_onboarding_node(state: AgentState) -> Dict[str, Any]:
    """Step 3f-h: Generates Offer Letter, executes BGV, and builds Onboarding Package."""
    screening = state.get("screening_report", {})
    candidate_name = screening.get("candidate_name", "Dr. Eleanor Vance")
    role_title = "Senior AI & LangGraph Engineer"
    api_key = state.get("api_key")
    model_name = state.get("model_name")

    # Refined System Prompt for OfferLetter
    system_prompt = (
        "You are an Executive Compensation & HR Operations Manager. "
        "Generate a formal Offer Letter JSON with exact fields: candidate_name, role_title, offered_ctc, "
        "joining_bonus, work_mode, office_location, date_of_joining, and offer_letter_text."
    )

    offer: OfferLetter = generate_structured_output(
        system_prompt=system_prompt,
        user_prompt=f"Candidate: {candidate_name}, Role: {role_title}, Compensation: 24 LPA",
        output_schema=OfferLetter,
        api_key=api_key,
        model_name=model_name
    )

    bgv = BackgroundVerificationTool.execute_bgv_check(candidate_name)
    onboarding = OnboardingTool.generate_onboarding_package(candidate_name, role_title, offer.date_of_joining)

    log_entry = {
        "step_name": "Step 3: Offer, BGV & Onboarding Complete",
        "node_id": "offer_and_onboarding_node",
        "detail": f"Offer issued ({offer.offered_ctc}), BGV: {bgv.overall_bgv_status}, Onboarding Ready!",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }

    logs = list(state.get("execution_logs", []))
    logs.append(log_entry)

    return {
        "official_offer_letter": offer.model_dump(),
        "bgv_report": bgv.model_dump(),
        "onboarding_package": onboarding.model_dump(),
        "execution_logs": logs,
        "is_complete": True
    }

def build_recruitment_graph() -> StateGraph:
    """Builds and compiles the full 3-step recruitment lifecycle state machine."""
    workflow = StateGraph(AgentState)

    workflow.add_node("job_intake_node", job_intake_node)
    workflow.add_node("sourcing_posting_node", sourcing_posting_node)
    workflow.add_node("screener_node", screener_node)
    workflow.add_node("evaluator_node", evaluator_node)
    workflow.add_node("shortlist_email_node", shortlist_email_node)
    workflow.add_node("telephonic_screening_node", telephonic_screening_node)
    workflow.add_node("offer_and_onboarding_node", offer_and_onboarding_node)

    workflow.set_entry_point("job_intake_node")
    workflow.add_edge("job_intake_node", "sourcing_posting_node")
    workflow.add_edge("sourcing_posting_node", "screener_node")
    workflow.add_edge("screener_node", "evaluator_node")

    workflow.add_conditional_edges(
        "evaluator_node",
        should_continue_screening,
        {
            "screener_node": "screener_node",
            "shortlist_email_node": "shortlist_email_node"
        }
    )

    workflow.add_edge("shortlist_email_node", "telephonic_screening_node")
    workflow.add_edge("telephonic_screening_node", "offer_and_onboarding_node")
    workflow.add_edge("offer_and_onboarding_node", END)

    return workflow.compile()
