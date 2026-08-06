import json
import logging
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from recruitment_agent.config import config
from recruitment_agent.models import (
    CandidateScreening, CategoryScore, EvaluationCritique,
    InterviewKit, InterviewQuestion, JobIntakePlan, OfferLetter
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

def get_llm(api_key: Optional[str] = None, model_name: Optional[str] = None, base_url: Optional[str] = None) -> ChatOpenAI:
    """Returns a ChatOpenAI instance pointing to DeepSeek API."""
    key = api_key if api_key else config.DEEPSEEK_API_KEY
    url = base_url if base_url else config.DEEPSEEK_BASE_URL
    model = model_name if model_name else config.DEEPSEEK_MODEL

    return ChatOpenAI(
        model=model,
        openai_api_key=key if key else "dummy_key_for_mock",
        openai_api_base=url,
        temperature=0.2,
        max_tokens=4000,
    )

def generate_structured_output(
    system_prompt: str,
    user_prompt: str,
    output_schema: Type[T],
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> T:
    """
    Invokes DeepSeek LLM with structured output formatting.
    Falls back gracefully to intelligent mock output if API key is missing or fails.
    """
    key = api_key if api_key else config.DEEPSEEK_API_KEY
    
    if not key or key.strip() == "" or key == "your_deepseek_api_key_here":
        logger.warning("No valid DeepSeek API key provided. Using Mock LLM engine.")
        return _generate_mock_output(output_schema, user_prompt)
        
    try:
        llm = get_llm(api_key=key, model_name=model_name)
        
        schema_json = json.dumps(output_schema.model_json_schema(), indent=2)
        full_system_prompt = (
            f"{system_prompt}\n\n"
            f"IMPORTANT: You MUST respond ONLY with valid JSON strictly matching this schema:\n"
            f"```json\n{schema_json}\n```\n"
            f"Do not include any text outside of the raw JSON code block."
        )
        
        messages = [
            SystemMessage(content=full_system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        content = response.content.strip()
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        data = json.loads(content)
        return output_schema.model_validate(data)
        
    except Exception as e:
        logger.error(f"Error calling DeepSeek API: {e}. Falling back to mock generator.")
        return _generate_mock_output(output_schema, user_prompt)

def _generate_mock_output(output_schema: Type[T], prompt: str) -> T:
    """Mock generator for demonstration when API key is unconfigured."""
    prompt_lower = prompt.lower()
    
    if output_schema == JobIntakePlan:
        return JobIntakePlan(
            role_title="Senior AI & LangGraph Engineer",
            department="Artificial Intelligence R&D",
            key_skills_needed=["LangGraph", "Python 3.11", "DeepSeek API", "Pydantic", "FastAPI", "Docker"],
            generated_job_description="""
JOB TITLE: Senior AI & LangGraph Engineer
DEPARTMENT: Artificial Intelligence R&D
LOCATION: Remote / Hybrid

ROLES & RESPONSIBILITIES:
- Architect, build, and deploy production-grade multi-agent AI systems using LangGraph, LangChain, and Python 3.11+.
- Design dynamic self-correction and evaluation loops to ensure high-accuracy structured LLM outputs.
- Integrate open-source and commercial LLM APIs (DeepSeek, OpenAI) with optimized prompts and JSON schema constraints.
- Collaborate with product and HR leadership to automate talent selection pipelines.

REQUIRED QUALIFICATIONS:
- 5+ years of software engineering experience with at least 2+ years building LLM-powered applications.
- Strong proficiency in Python, Pydantic, Asyncio, and FastAPI/Gradio.
- Direct experience implementing LangGraph cyclic graphs, state management, and custom evaluators.
- Bachelor's degree or higher in Computer Science or related STEM field.
""",
            min_salary_band="18 LPA",
            max_salary_band="28 LPA",
            currency="INR"
        )
        
    elif output_schema == CandidateScreening:
        if "weak candidate" in prompt_lower or "junior" in prompt_lower:
            return CandidateScreening(
                candidate_name="Alex Mercer",
                candidate_email="alex.mercer@devmail.com",
                overall_match_score=58,
                recommendation="HOLD",
                executive_summary="Alex presents a solid foundation in basic software development but falls short of the required senior experience level and specialized AI system depth specified.",
                experience_fit_commentary="Candidate has ~3.5 years experience vs the required 5+ years senior requirement. Gap of ~1.5 years.",
                work_mode_and_location_fit="Candidate prefers Hybrid/Remote in Austin, TX.",
                salary_expectation_fit="14 LPA (Within budget)",
                key_qualifications=[
                    "3.5 years Python programming experience",
                    "Basic REST API integration skills",
                    "Familiarity with Git and Docker containers"
                ],
                critical_gaps=[
                    "Missing 5+ years required senior lead experience",
                    "No experience with LangChain, LangGraph, or multi-agent architectures"
                ],
                category_scores=[
                    CategoryScore(
                        category="Technical Skills",
                        score=60,
                        strengths=["Python proficiency", "Git"],
                        gaps=["LangGraph", "Vector DBs"],
                        summary="Meets baseline Python requirements."
                    ),
                    CategoryScore(
                        category="Experience Fit",
                        score=55,
                        strengths=["Mid-level API development"],
                        gaps=["Architectural leadership"],
                        summary="Experience level is mid-tier (3.5 yrs) vs required Senior (5+ yrs)."
                    )
                ]
            )
        else:
            return CandidateScreening(
                candidate_name="Dr. Eleanor Vance",
                candidate_email="eleanor.vance@ai-research-lab.io",
                overall_match_score=92,
                recommendation="STRONG_PASS",
                executive_summary="Dr. Eleanor Vance is an exceptional candidate. She brings 7.5 years of hands-on experience designing distributed LLM applications, custom LangGraph workflows, and scalable vector search pipelines.",
                experience_fit_commentary="Candidate possesses 7.5 years of experience, exceeding the 5+ years requirement.",
                work_mode_and_location_fit="Candidate is located in San Francisco, CA and prefers Remote / Hybrid work mode. Fully aligns with target criteria.",
                salary_expectation_fit="24 LPA (Well within 18-28 LPA target band)",
                key_qualifications=[
                    "7.5 years Senior AI Engineering background (Exceeds 5+ yrs requirement)",
                    "Deep mastery of LangGraph, LangChain, Pydantic, and DeepSeek API integrations",
                    "Proven track record scaling LLM microservices handling 15M+ daily requests",
                    "Ph.D. in Computer Science from Stanford University"
                ],
                critical_gaps=[
                    "Primarily AWS-focused; JD specifies GCP & Azure preference"
                ],
                category_scores=[
                    CategoryScore(
                        category="Technical Skills",
                        score=95,
                        strengths=["LangGraph expertise", "Python 3.11+", "DeepSeek API"],
                        gaps=["GCP Cloud Platform"],
                        summary="Outstanding technical alignment with core AI stack."
                    ),
                    CategoryScore(
                        category="Experience Fit",
                        score=92,
                        strengths=["7.5 years total experience", "Led 6 AI engineers"],
                        gaps=[],
                        summary="Exceeds senior level experience requirement."
                    )
                ]
            )
            
    elif output_schema == EvaluationCritique:
        return EvaluationCritique(
            quality_score=94,
            needs_revision=False,
            critique_notes=[
                "Screening report is comprehensive, evidence-backed, and accurately evaluates experience level, work mode preferences, and salary expectations."
            ],
            focus_areas_for_refinement=[]
        )

    elif output_schema == OfferLetter:
        return OfferLetter(
            candidate_name="Dr. Eleanor Vance",
            role_title="Senior AI & LangGraph Engineer",
            offered_ctc="24,00,000 INR per annum (24 LPA)",
            joining_bonus="2,00,000 INR (Joining Bonus)",
            work_mode="Remote / Hybrid",
            office_location="Bengaluru / San Francisco / Remote",
            date_of_joining="1st September 2026",
            offer_letter_text="""
FORMAL OFFER OF EMPLOYMENT

Date: August 6, 2026
Candidate Name: Dr. Eleanor Vance

Dear Eleanor,

We are delighted to offer you the full-time position of Senior AI & LangGraph Engineer. 

COMPENSATION & BENEFIT HIGHLIGHTS:
- Annual Fixed Compensation (CTC): INR 24,00,000 (Twenty-Four Lakhs per annum)
- One-time Signing / Joining Bonus: INR 2,00,000
- Work Mode: Remote / Hybrid
- Date of Joining: September 1, 2026

We look forward to welcome you to our AI R&D Engineering Team!

Sincerely,
Director of Human Resources & Talent Acquisition
"""
        )
            
    elif output_schema == InterviewKit:
        return InterviewKit(
            candidate_name="Dr. Eleanor Vance",
            suggested_role_level="Lead / Senior AI Engineer",
            interview_focus="System Architecture, State Graph Management, and Error Recovery in LangGraph",
            questions=[
                InterviewQuestion(
                    question_type="Technical",
                    topic="LangGraph State Persistence & Reflection Loops",
                    question_text="Can you describe how you implement cyclic nodes and checkpointing in LangGraph to prevent infinite loops during self-correction?",
                    why_asked="Candidate claims 7+ years AI experience and LangGraph mastery.",
                    ideal_answer_rubric="Should mention typed dictionary state, recursion limits, conditional routing functions, and checkpointers."
                )
            ],
            overall_hiring_advice="Proceed to Technical Onsite Interview immediately. High priority candidate with excellent alignment."
        )

    return output_schema.model_construct()
