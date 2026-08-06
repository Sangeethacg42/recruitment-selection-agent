from typing import Dict, Any

ROLE_PRESETS: Dict[str, Dict[str, str]] = {
    "Senior AI & LangGraph Engineer": {
        "department": "Artificial Intelligence R&D",
        "skills": "LangGraph, Python 3.11, DeepSeek API, Pydantic, FastAPI, Docker, Vector DBs",
        "min_salary": "18 LPA",
        "max_salary": "28 LPA"
    },
    "Lead Full-Stack Developer (React + Python)": {
        "department": "Engineering & Technology",
        "skills": "TypeScript, React, Next.js, Python, FastAPI, PostgreSQL, Docker, AWS",
        "min_salary": "20 LPA",
        "max_salary": "32 LPA"
    },
    "Senior Data Scientist & MLOps": {
        "department": "Data Science & Analytics",
        "skills": "Python, PyTorch, MLflow, Scikit-Learn, DeepSeek API, SQL, Kubernetes",
        "min_salary": "16 LPA",
        "max_salary": "26 LPA"
    },
    "GenAI Product Manager": {
        "department": "Product Management",
        "skills": "Product Roadmap, LLM System Architecture, Agile, User Research, A/B Testing",
        "min_salary": "22 LPA",
        "max_salary": "35 LPA"
    },
    "DevOps & Cloud Infrastructure Architect": {
        "department": "Cloud & Infrastructure",
        "skills": "Docker, Kubernetes, Terraform, AWS, Azure, CI/CD Pipelines, Bash",
        "min_salary": "18 LPA",
        "max_salary": "30 LPA"
    },
    "HR Talent Acquisition Specialist": {
        "department": "Human Resources & People Ops",
        "skills": "Technical Sourcing, Resume Screening, Salary Negotiation, ATS Management, Candidate Interviewing",
        "min_salary": "10 LPA",
        "max_salary": "18 LPA"
    }
}

SAMPLE_JOB_DESCRIPTIONS: Dict[str, str] = {
    "Senior AI & LangGraph Engineer": """
JOB TITLE: Senior AI & LangGraph Engineer
DEPARTMENT: Artificial Intelligence R&D
LOCATION: Remote / Hybrid

ROLES & RESPONSIBILITIES:
- Architect, build, and deploy production-grade multi-agent AI systems using LangGraph, LangChain, and Python 3.11+.
- Design dynamic self-correction and evaluation loops to ensure high-accuracy structured LLM outputs.
- Integrate open-source and commercial LLM APIs (DeepSeek, OpenAI) with optimized prompts and JSON schema constraints.
- Build microservices for resume parsing, semantic search, and candidate scoring.
- Collaborate with product and HR leadership to automate talent selection pipelines.

REQUIRED QUALIFICATIONS:
- 5+ years of software engineering experience with at least 2+ years building LLM-powered applications.
- Strong proficiency in Python, Pydantic, Asyncio, and FastAPI/Gradio.
- Direct experience implementing LangGraph cyclic graphs, state management, and custom evaluators.
- Bachelor's degree or higher in Computer Science or related STEM field.
""",

    "Lead Full-Stack Web Developer (React + Python)": """
JOB TITLE: Lead Full-Stack Web Developer
DEPARTMENT: Engineering & Technology
LOCATION: Remote

ROLES & RESPONSIBILITIES:
- Lead the end-to-end development of customer-facing web applications using React / Next.js and Python backend APIs.
- Implement responsive, accessible UI designs with CSS modern frameworks and component libraries.
- Optimize database queries, API caching, and microservice architectures.

REQUIRED QUALIFICATIONS:
- 6+ years of full-stack web application development experience.
- Expert knowledge of TypeScript, React, HTML5/CSS3, and Python (FastAPI/Django).
"""
}

SAMPLE_RESUMES: Dict[str, str] = {
    "Dr. Eleanor Vance (Strong Fit - Senior AI)": """
DR. ELEANOR VANCE
San Francisco, CA | eleanor.vance@ai-research-lab.io

EXECUTIVE SUMMARY:
Senior AI Architect and Computer Scientist with 7.5 years of experience leading engineering teams in designing multi-agent LLM systems, self-correcting graphs, and enterprise AI automation tools. Expert in LangGraph, Python, Pydantic, and DeepSeek/OpenAI integrations.

WORK EXPERIENCE:
Lead AI Engineer | Apex Intelligence (2022 - Present)
- Designed and launched autonomous enterprise workflow platforms built on LangGraph and Python 3.11, handling 15M daily requests.
- Engineered iterative reflection and evaluation loops that improved structured extraction accuracy from 74% to 96.8%.
- Integrated DeepSeek API and OpenAI models with fallbacks.

EDUCATION:
- Ph.D. in Computer Science, Stanford University (2019)
- B.S. in Computer Engineering, UC Berkeley (2015)
""",

    "Alex Mercer (Partial Fit - Mid Level Dev)": """
ALEX MERCER
Austin, TX | alex.mercer@devmail.com

SUMMARY:
Software Developer with 3.5 years of experience in Python web development, API integrations, and basic database management.

EXPERIENCE:
Software Engineer | WebTech Solutions (2022 - Present)
- Built backend REST APIs in Python using Flask and Docker.

EDUCATION:
- B.S. in Computer Science, University of Texas at Austin (2021)
"""
}
