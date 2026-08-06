import datetime
import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from recruitment_agent.config import config
from recruitment_agent.models import (
    AgentState, CandidateScreening, EvaluationCritique, InterviewKit
)
from recruitment_agent.llm import generate_structured_output

logger = logging.getLogger(__name__)

def screener_node(state: AgentState) -> Dict[str, Any]:
    """Node 1: Evaluates candidate resume against Job Description."""
    jd = state.get("job_description", "")
    resume = state.get("candidate_resume", "")
    critique = state.get("critique")
    reflection_count = state.get("reflection_count", 0)
    api_key = state.get("api_key")
    model_name = state.get("model_name")

    system_prompt = (
        "You are an expert Senior Technical Talent Acquisition Specialist and Executive Recruiter. "
        "Analyze the provided candidate resume thoroughly against the Job Description. "
        "Be rigorous, evidence-based, and precise. Identify specific technical capabilities, years of experience, "
        "education, and dealbreaker gaps."
    )
    
    if critique and critique.get("needs_revision"):
        notes = "\n- ".join(critique.get("critique_notes", []))
        system_prompt += (
            f"\n\nREVISION INSTRUCTIONS (Reflection Iteration {reflection_count}):\n"
            f"Your previous screening was evaluated by QA HR Audit and received the following critique:\n- {notes}\n"
            f"Address all critique points directly and refine your analysis for maximum depth and accuracy."
        )

    user_prompt = f"JOB DESCRIPTION:\n{jd}\n\nCANDIDATE RESUME:\n{resume}"

    screening: CandidateScreening = generate_structured_output(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output_schema=CandidateScreening,
        api_key=api_key,
        model_name=model_name
    )

    log_entry = {
        "step_name": f"Screening Analysis (Pass {reflection_count + 1})",
        "node_id": "screener_node",
        "detail": f"Screening complete. Score: {screening.overall_match_score}/100, Rec: {screening.recommendation}",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }

    logs = list(state.get("execution_logs", []))
    logs.append(log_entry)

    return {
        "screening_report": screening.model_dump(),
        "execution_logs": logs
    }

def evaluator_node(state: AgentState) -> Dict[str, Any]:
    """Node 2 (Reflection Loop): QA Audit evaluating screening report quality."""
    jd = state.get("job_description", "")
    resume = state.get("candidate_resume", "")
    screening_dict = state.get("screening_report", {})
    reflection_count = state.get("reflection_count", 0)
    api_key = state.get("api_key")
    model_name = state.get("model_name")

    system_prompt = (
        "You are a Director of HR & Talent Audit Quality Assurance. "
        "Your task is to audit the initial Candidate Screening Report against the original Job Description and Resume. "
        "Critique whether the screening missed key requirements, formed unsubstantiated assumptions, "
        "or lacked depth in category scoring."
    )

    user_prompt = (
        f"JOB DESCRIPTION:\n{jd}\n\n"
        f"CANDIDATE RESUME:\n{resume}\n\n"
        f"CURRENT SCREENING REPORT:\n{screening_dict}\n\n"
        f"CURRENT REFLECTION ITERATION: {reflection_count}"
    )

    critique: EvaluationCritique = generate_structured_output(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output_schema=EvaluationCritique,
        api_key=api_key,
        model_name=model_name
    )

    new_reflection_count = reflection_count + 1
    
    log_entry = {
        "step_name": f"QA Reflection Audit #{new_reflection_count}",
        "node_id": "evaluator_node",
        "detail": f"Audit Quality Score: {critique.quality_score}/100. Needs Revision: {critique.needs_revision}",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }

    logs = list(state.get("execution_logs", []))
    logs.append(log_entry)

    return {
        "critique": critique.model_dump(),
        "reflection_count": new_reflection_count,
        "execution_logs": logs
    }

def should_continue(state: AgentState) -> Literal["screener_node", "interview_gen_node"]:
    """Conditional Edge: Determines whether to loop back for refinement or finalize."""
    critique = state.get("critique", {})
    reflection_count = state.get("reflection_count", 0)

    needs_revision = critique.get("needs_revision", False)
    quality_score = critique.get("quality_score", 100)

    # Loop back if quality < MIN_PASSING_SCORE or needs revision, up to MAX_REFLECTION_LOOPS
    if (needs_revision or quality_score < config.MIN_PASSING_SCORE) and reflection_count < config.MAX_REFLECTION_LOOPS:
        logger.info(f"Looping back to screener_node (Reflection {reflection_count}/{config.MAX_REFLECTION_LOOPS})")
        return "screener_node"
    
    logger.info("Proceeding to interview kit generation node.")
    return "interview_gen_node"

def interview_gen_node(state: AgentState) -> Dict[str, Any]:
    """Node 3: Generates targeted Interview Question Kit and Hiring Advice."""
    jd = state.get("job_description", "")
    screening_dict = state.get("screening_report", {})
    api_key = state.get("api_key")
    model_name = state.get("model_name")

    system_prompt = (
        "You are an Executive Hiring Committee Manager. "
        "Based on the final candidate screening report and job description, construct a customized, highly targeted "
        "interview kit. Create technical, behavioral, and practical questions specifically designed to probe candidate "
        "gaps and confirm candidate strengths."
    )

    user_prompt = f"JOB DESCRIPTION:\n{jd}\n\nSCREENING REPORT:\n{screening_dict}"

    interview_kit: InterviewKit = generate_structured_output(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output_schema=InterviewKit,
        api_key=api_key,
        model_name=model_name
    )

    log_entry = {
        "step_name": "Interview Kit Generation",
        "node_id": "interview_gen_node",
        "detail": f"Generated {len(interview_kit.questions)} targeted questions and interview strategy.",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }

    logs = list(state.get("execution_logs", []))
    logs.append(log_entry)

    return {
        "interview_kit": interview_kit.model_dump(),
        "execution_logs": logs,
        "is_complete": True
    }

def build_recruitment_graph() -> StateGraph:
    """Builds and compiles the LangGraph state machine with reflection loop."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("screener_node", screener_node)
    workflow.add_node("evaluator_node", evaluator_node)
    workflow.add_node("interview_gen_node", interview_gen_node)

    # Set entry point
    workflow.set_entry_point("screener_node")

    # Add edge from screener to evaluator node
    workflow.add_edge("screener_node", "evaluator_node")

    # Add conditional loop edge from evaluator node
    workflow.add_conditional_edges(
        "evaluator_node",
        should_continue,
        {
            "screener_node": "screener_node",
            "interview_gen_node": "interview_gen_node"
        }
    )

    # Add edge from interview generator to end
    workflow.add_edge("interview_gen_node", END)

    return workflow.compile()
