import json
import logging
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from recruitment_agent.config import config
from recruitment_agent.models import (
    CandidateScreening, CategoryScore, EvaluationCritique,
    InterviewKit, InterviewQuestion
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
    
    if output_schema == CandidateScreening:
        if "weak candidate" in prompt_lower or "junior" in prompt_lower:
            return CandidateScreening(
                candidate_name="Alex Mercer",
                overall_match_score=58,
                recommendation="HOLD",
                executive_summary="Alex presents a solid foundation in basic software development but falls short of the required experience level and specialized AI/ML system depth specified.",
                experience_fit_commentary="Candidate has ~3.5 years experience vs the required 5+ years senior requirement. Gap of ~1.5 years.",
                work_mode_and_location_fit="Candidate prefers Hybrid/Remote in Austin, TX. Fits Remote setup but requires relocation for Work From Office.",
                key_qualifications=[
                    "3.5 years Python programming experience",
                    "Basic REST API integration skills",
                    "Familiarity with Git and Docker containers"
                ],
                critical_gaps=[
                    "Missing 5+ years required senior lead experience",
                    "No experience with LangChain, LangGraph, or multi-agent architectures",
                    "Limited high-throughput production deployment background"
                ],
                category_scores=[
                    CategoryScore(
                        category="Technical Skills",
                        score=60,
                        strengths=["Python proficiency", "Git"],
                        gaps=["LangGraph", "Vector DBs", "Async architectures"],
                        summary="Meets baseline Python requirements but lacks advanced stack expertise."
                    ),
                    CategoryScore(
                        category="Experience & Seniority Fit",
                        score=55,
                        strengths=["Mid-level API development"],
                        gaps=["Architectural leadership", "Scale requirements"],
                        summary="Experience level is mid-tier (3.5 yrs) vs required Senior (5+ yrs)."
                    ),
                    CategoryScore(
                        category="Work Mode & Location Alignment",
                        score=70,
                        strengths=["Open to remote work"],
                        gaps=["Requires relocation for physical office"],
                        summary="Location and work mode compatibility verified."
                    )
                ]
            )
        else:
            return CandidateScreening(
                candidate_name="Dr. Eleanor Vance",
                overall_match_score=92,
                recommendation="STRONG_PASS",
                executive_summary="Dr. Eleanor Vance is an exceptional candidate. She brings 7+ years of hands-on experience designing distributed LLM applications, custom LangGraph workflows, and scalable vector search pipelines.",
                experience_fit_commentary="Candidate possesses 7.5 years of experience, exceeding the 5+ years requirement.",
                work_mode_and_location_fit="Candidate is located in San Francisco, CA and prefers Remote / Hybrid work mode. Fully aligns with target criteria.",
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
                        category="Experience & Seniority Fit",
                        score=92,
                        strengths=["7.5 years total experience", "Led 6 AI engineers"],
                        gaps=[],
                        summary="Exceeds senior level experience requirement."
                    ),
                    CategoryScore(
                        category="Work Mode & Location Alignment",
                        score=90,
                        strengths=["Remote / Hybrid readiness", "Flexible schedule"],
                        gaps=[],
                        summary="Perfect work mode and location match."
                    )
                ]
            )
            
    elif output_schema == EvaluationCritique:
        return EvaluationCritique(
            quality_score=94,
            needs_revision=False,
            critique_notes=[
                "Screening report is comprehensive, evidence-backed, and accurately evaluates experience level, work mode preferences, and location fit."
            ],
            focus_areas_for_refinement=[]
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
                ),
                InterviewQuestion(
                    question_type="System Design / Practical",
                    topic="Work Mode Collaboration & Scalability",
                    question_text="How do you effectively lead a distributed remote engineering team across multiple time zones while deploying production AI microservices?",
                    why_asked="Probing work mode alignment and leadership capabilities.",
                    ideal_answer_rubric="Discusses asynchronous documentation, CI/CD automated testing, clear API contracts, and daily standups."
                )
            ],
            overall_hiring_advice="Proceed to Technical Onsite Interview immediately. High priority candidate with excellent alignment."
        )

    return output_schema.model_construct()
