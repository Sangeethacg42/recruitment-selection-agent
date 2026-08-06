import os
import glob
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class SourcedCandidate(BaseModel):
    source_platform: str = Field(description="Platform name e.g. LinkedIn, Naukri, Indeed, Foundit, Local Folder")
    profile_id: str
    candidate_name: str
    current_title: str
    headline_or_summary: str
    experience_years: str
    location: str
    key_skills: List[str]
    raw_resume_text: str

class SourcingTools:
    """Tools for fetching candidates from job portals and local folders."""

    @staticmethod
    def fetch_from_linkedin(search_query: str, location: str = "Remote", limit: int = 3) -> List[SourcedCandidate]:
        """Simulates fetching top candidate profiles from LinkedIn Recruiter API."""
        logger.info(f"Searching LinkedIn for '{search_query}' in '{location}'...")
        
        candidates = [
            SourcedCandidate(
                source_platform="LinkedIn",
                profile_id="in-eleanor-vance-99",
                candidate_name="Dr. Eleanor Vance",
                current_title="Lead AI & Machine Learning Engineer at Apex Intelligence",
                headline_or_summary="Ph.D. in CS | 7+ yrs building LangGraph state machines, DeepSeek API pipelines, and RAG vector search microservices.",
                experience_years="7.5 years",
                location="San Francisco, CA (Remote eligible)",
                key_skills=["LangGraph", "Python 3.11", "DeepSeek API", "Pydantic", "Vector DBs", "Docker"],
                raw_resume_text="""
DR. ELEANOR VANCE
LinkedIn: linkedin.com/in/eleanor-vance-ai | San Francisco, CA

SUMMARY:
Lead AI Engineer with 7.5 years experience designing multi-agent workflows, autonomous reflection loops, and high-throughput vector search microservices.

EXPERIENCE:
Lead AI Engineer | Apex Intelligence (2022 - Present)
- Built autonomous LangGraph evaluation loops reducing LLM error rate by 82%.
- Integrated DeepSeek API for automated candidate parsing.
- Managed team of 6 engineers.

EDUCATION:
- Ph.D. in Computer Science, Stanford University (2019)
- B.S. CS, UC Berkeley (2015)
"""
            ),
            SourcedCandidate(
                source_platform="LinkedIn",
                profile_id="in-marcus-dev-42",
                candidate_name="Marcus Thorne",
                current_title="Senior Full Stack & AI Developer at CloudScale",
                headline_or_summary="6 yrs experience | Python, FastAPI, React, LangChain, OpenAI, and DeepSeek API deployments.",
                experience_years="6 years",
                location="Seattle, WA",
                key_skills=["Python", "FastAPI", "React", "LangChain", "DeepSeek API", "PostgreSQL"],
                raw_resume_text="""
MARCUS THORNE
LinkedIn: linkedin.com/in/marcus-thorne-dev | Seattle, WA

SUMMARY:
Senior Full Stack Developer specializing in AI-native web applications, API microservices, and React frontends.

EXPERIENCE:
Senior Developer | CloudScale (2021 - Present)
- Developed AI agent dashboards using Gradio and React.
- Built backend APIs integrating DeepSeek-chat and OpenAI endpoints.

EDUCATION:
- B.S. Software Engineering, University of Washington (2018)
"""
            )
        ]
        return candidates[:limit]

    @staticmethod
    def fetch_from_naukri(search_query: str, experience_range: str = "3-8 yrs", location: str = "India / Remote", limit: int = 3) -> List[SourcedCandidate]:
        """Simulates fetching candidates from Naukri India portal."""
        logger.info(f"Searching Naukri for '{search_query}' with experience '{experience_range}'...")
        
        candidates = [
            SourcedCandidate(
                source_platform="Naukri",
                profile_id="nk-priya-sharma-101",
                candidate_name="Priya Sharma",
                current_title="Senior AI Solution Architect",
                headline_or_summary="Senior Architect with 6.5 years experience in NLP, Python, LangGraph agent workflows, and cloud AI deployments.",
                experience_years="6.5 years",
                location="Bengaluru, India",
                key_skills=["Python", "LangGraph", "DeepSeek API", "FastAPI", "Azure AI", "LangChain"],
                raw_resume_text="""
PRIYA SHARMA
Naukri Profile ID: NK-PRIYA-101 | Bengaluru, KA

SUMMARY:
Senior AI Solution Architect with 6.5 years experience delivering enterprise LLM solutions, automated resume screeners, and LangGraph multi-agent pipelines.

EXPERIENCE:
Senior AI Architect | TechSolutions India (2021 - Present)
- Architected automated HR screening workflows using Python and LangGraph.
- Reduced candidate evaluation turnaround time by 75%.

EDUCATION:
- M.Tech in Artificial Intelligence, IIT Madras (2018)
- B.Tech in CS, NIT Trichy (2016)
"""
            ),
            SourcedCandidate(
                source_platform="Naukri",
                profile_id="nk-rohit-verma-204",
                candidate_name="Rohit Verma",
                current_title="Lead Data Scientist & GenAI Lead",
                headline_or_summary="5 years building LLM fine-tuning pipelines, DeepSeek API integrations, and HR tech analytics.",
                experience_years="5 years",
                location="Hyderabad, India",
                key_skills=["Python", "DeepSeek", "PyTorch", "Gradio", "RAG", "SQL"],
                raw_resume_text="""
ROHIT VERMA
Naukri Profile ID: NK-ROHIT-204 | Hyderabad, TS

SUMMARY:
Lead Data Scientist specializing in Generative AI, prompt engineering, and custom evaluation loops.

EXPERIENCE:
GenAI Lead | DataCorp India (2022 - Present)
- Designed automated recruitment screening models with custom rubric scoring.

EDUCATION:
- B.Tech in Computer Science, BITS Pilani (2019)
"""
            )
        ]
        return candidates[:limit]

    @staticmethod
    def fetch_from_indeed(search_query: str, location: str = "Remote", limit: int = 3) -> List[SourcedCandidate]:
        """Simulates fetching candidate profiles from Indeed Resume Search."""
        logger.info(f"Searching Indeed for '{search_query}'...")
        
        candidates = [
            SourcedCandidate(
                source_platform="Indeed",
                profile_id="ind-samuel-reed-77",
                candidate_name="Samuel Reed",
                current_title="Senior Python & Automation Specialist",
                headline_or_summary="5+ years in Python backend development, web scrapers, API integrations, and AI workflow automation.",
                experience_years="5.2 years",
                location="Austin, TX",
                key_skills=["Python", "FastAPI", "Automation", "OpenAI API", "Docker", "Git"],
                raw_resume_text="""
SAMUEL REED
Indeed Resume ID: IND-SAM-77 | Austin, TX

SUMMARY:
Python Developer focused on workflow automation, API integration, and machine learning infrastructure.

EXPERIENCE:
Automation Engineer | AutoTech Innovations (2020 - Present)
- Built automated background processing pipelines in Python.

EDUCATION:
- B.S. CS, UT Austin (2019)
"""
            )
        ]
        return candidates[:limit]

    @staticmethod
    def fetch_from_foundit(search_query: str, location: str = "India", limit: int = 3) -> List[SourcedCandidate]:
        """Simulates fetching candidate profiles from Foundit (formerly Monster India)."""
        logger.info(f"Searching Foundit for '{search_query}'...")
        
        candidates = [
            SourcedCandidate(
                source_platform="Foundit",
                profile_id="fnd-aarav-patel-88",
                candidate_name="Aarav Patel",
                current_title="AI Application Developer",
                headline_or_summary="4 years building AI agent backends with Python, LangGraph, and Gradio frontends.",
                experience_years="4 years",
                location="Mumbai, India",
                key_skills=["Python", "LangGraph", "Gradio", "DeepSeek", "MongoDB"],
                raw_resume_text="""
AARAV PATEL
Foundit ID: FND-AARAV-88 | Mumbai, MH

SUMMARY:
AI Developer with hands-on experience building LangGraph state machines and interactive Gradio user interfaces.

EXPERIENCE:
AI Software Developer | NextGen Apps (2022 - Present)
- Developed Gradio prototypes for recruitment automation.

EDUCATION:
- B.E. CS, Mumbai University (2020)
"""
            )
        ]
        return candidates[:limit]

    @staticmethod
    def fetch_from_local_folder(folder_path: str) -> List[SourcedCandidate]:
        """Reads candidate resumes directly from local text, markdown, or pdf files in a folder."""
        logger.info(f"Scanning local folder for resume files: '{folder_path}'")
        candidates = []
        
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            logger.warning(f"Local folder path does not exist or is invalid: {folder_path}")
            return candidates

        # Find txt, md, or doc files
        file_patterns = ["*.txt", "*.md", "*.doc"]
        found_files = []
        for pattern in file_patterns:
            found_files.extend(glob.glob(os.path.join(folder_path, pattern)))
            found_files.extend(glob.glob(os.path.join(folder_path, "**", pattern), recursive=True))
            
        for filepath in found_files[:10]:  # Limit to max 10 files per batch
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                    
                if not content:
                    continue
                    
                filename = os.path.basename(filepath)
                name_clean = filename.rsplit(".", 1)[0].replace("_", " ").title()
                
                candidates.append(
                    SourcedCandidate(
                        source_platform="Local Folder",
                        profile_id=f"file://{filepath}",
                        candidate_name=name_clean,
                        current_title="Ingested Candidate File",
                        headline_or_summary=f"Resume file ingested from {filename}",
                        experience_years="Extracted via screening",
                        location="Local System",
                        key_skills=["Extracted from local resume"],
                        raw_resume_text=content
                    )
                )
            except Exception as e:
                logger.error(f"Error reading local resume file '{filepath}': {e}")
                
        return candidates
