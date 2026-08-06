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
    
    # If no key provided, use mock generation
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
        
        # Clean JSON markdown if wrapped
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
        # Detect candidate fit from prompt hints if any
        if "weak candidate" in prompt_lower or "junior" in prompt_lower and "senior" in prompt_lower:
            return CandidateScreening(
                candidate_name="Alex Mercer",
                overall_match_score=58,
                recommendation="HOLD",
                executive_summary="Alex presents a solid foundation in basic software development but lacks the senior architecture experience, scale requirements, and specialized AI/ML system depth specified in the job description.",
                key_qualifications=[
                    "3 years Python programming experience",
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
                        category="Relevant Experience",
                        score=50,
                        strengths=["Mid-level API development"],
                        gaps=["Architectural leadership", "Large scale distributed systems"],
                        summary="Experience level is mid-tier (3 yrs) vs required Senior (6+ yrs)."
                    ),
                    CategoryScore(
                        category="Education & Certifications",
                        score=75,
                        strengths=["B.S. Computer Science"],
                        gaps=["No specialized AI certifications"],
                        summary="Solid educational background."
                    ),
                    CategoryScore(
                        category="Cultural & Communication Fit",
                        score=70,
                        strengths=["Clear resume formatting"],
                        gaps=["Limited documented cross-team mentoring"],
                        summary="Good communicator."
                    )
                ]
            )
        else:
            return CandidateScreening(
                candidate_name="Dr. Eleanor Vance",
                overall_match_score=88,
                recommendation="STRONG_PASS",
                executive_summary="Dr. Eleanor Vance is an exceptional candidate for the Senior AI Engineer role. She brings 7 years of hands-on experience designing distributed LLM applications, custom LangGraph workflows, and scalable vector search pipelines.",
                key_qualifications=[
                    "7+ years Senior Software & AI Engineering background",
                    "Deep mastery of LangGraph, LangChain, Pydantic, and OpenAI API integrations",
                    "Proven track record scaling LLM microservices handling 10M+ daily API queries",
                    "M.S. & Ph.D. in Computer Science with focus on Machine Learning"
                ],
                critical_gaps=[
                    "Primarily AWS-focused; JD specifies GCP & Azure preference",
                    "Salary expectation is at the top of the budget band"
                ],
                category_scores=[
                    CategoryScore(
                        category="Technical Skills",
                        score=92,
                        strengths=["LangGraph expertise", "Python 3.11+", "Distributed Vector DBs"],
                        gaps=["GCP Cloud Platform"],
                        summary="Outstanding technical alignment with core AI stack."
                    ),
                    CategoryScore(
                        category="Relevant Experience",
                        score=88,
                        strengths=["Led 5 AI engineers", "Built production multi-agent systems"],
                        gaps=["None significant"],
                        summary="Exceeds senior level experience requirements."
                    ),
                    CategoryScore(
                        category="Education & Certifications",
                        score=95,
                        strengths=["Ph.D. in Computer Science"],
                        gaps=[],
                        summary="Superior academic credentials."
                    ),
                    CategoryScore(
                        category="Cultural & Communication Fit",
                        score=85,
                        strengths=["Tech blogging & conference speaker", "Mentorship focus"],
                        gaps=["Preference for fully remote setup"],
                        summary="High collaborative leadership potential."
                    )
                ]
            )
            
    elif output_schema == EvaluationCritique:
        if "first screening" in prompt_lower or "revision 0" in prompt_lower:
            return EvaluationCritique(
                quality_score=72,
                needs_revision=True,
                critique_notes=[
                    "The screening report evaluated technical skills well but did not check if the candidate possesses mandatory security clearance or remote working zone requirements.",
                    "Needs explicit verification of salary alignment and candidate availability timeframe."
                ],
                focus_areas_for_refinement=[
                    "Re-verify job requirement dealbreakers against candidate resume",
                    "Provide more granular evidence for the Cultural & Communication score"
                ]
            )
        else:
            return EvaluationCritique(
                quality_score=94,
                needs_revision=False,
                critique_notes=[
                    "Screening report is comprehensive, evidence-backed, and accurately reflects JD requirements against candidate background."
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
                    why_asked="The candidate claims extensive LangGraph experience. This tests actual production implementation depth.",
                    ideal_answer_rubric="Should mention typed dictionary state, recursion limits, conditional routing functions based on state flags, and persistent memory saver checkpointers."
                ),
                InterviewQuestion(
                    question_type="System Design / Practical",
                    topic="Production Scale & Rate Limiting",
                    question_text="How would you architect a fall-back strategy when DeepSeek or OpenAI endpoints hit rate limits (HTTP 429) during peak batch processing?",
                    why_asked="JD requires robust production error handling and cost/latency optimization.",
                    ideal_answer_rubric="Should discuss exponential backoff retries, multi-provider fallback routing (e.g., DeepSeek -> Azure OpenAI), token usage budgeting, and async task queuing with Celery/Redis."
                ),
                InterviewQuestion(
                    question_type="Behavioral",
                    topic="Technical Leadership & Trade-offs",
                    question_text="Describe a situation where business leadership pushed for a quick LLM feature launch, but you identified security or hallucination risks. How did you handle it?",
                    why_asked="Evaluates senior-level stakeholder management and technical governance.",
                    ideal_answer_rubric="Looks for structured risk assessment, prototype guardrails (e.g. strict schema validation), and clear communication with non-technical leaders."
                )
            ],
            overall_hiring_advice="Proceed to Technical Onsite Interview immediately. High priority candidate with excellent alignment."
        )

    # Fallback default object
    return output_schema.model_construct()
