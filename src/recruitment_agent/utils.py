from typing import Dict, Any

SAMPLE_JOB_DESCRIPTIONS: Dict[str, str] = {
    "Senior AI & LangGraph Engineer": """
JOB TITLE: Senior AI & LangGraph Engineer
DEPARTMENT: Artificial Intelligence R&D
LOCATION: Remote / Hybrid

ROLES & RESPONSIBILITIES:
- Architect, build, and deploy production-grade multi-agent AI systems using LangGraph, LangChain, and Python 3.11+.
- Design dynamic self-correction and evaluation loops to ensure high-accuracy structured LLM outputs.
- Integrate open-source and commercial LLM APIs (DeepSeek, OpenAI, Anthropic) with optimized prompts and JSON schema constraints.
- Build microservices for resume parsing, semantic search, and candidate scoring.
- Collaborate with product and HR leadership to automate talent selection pipelines.

REQUIRED QUALIFICATIONS:
- 5+ years of software engineering experience with at least 2+ years building LLM-powered applications.
- Strong proficiency in Python, Pydantic, Asyncio, and FastAPI/Gradio.
- Direct experience implementing LangGraph cyclic graphs, state management, and custom evaluators.
- Solid understanding of vector databases, embeddings, and RAG retrieval pipelines.
- Bachelor's degree or higher in Computer Science, Data Science, or related STEM field.

NICE TO HAVE:
- Experience with DeepSeek API or open-weights models (LLaMA 3, Qwen).
- Prior background in HR technology, recruitment ATS integration, or document parsing.
""",

    "Lead Full-Stack Web Developer (React + Python)": """
JOB TITLE: Lead Full-Stack Web Developer
DEPARTMENT: Engineering
LOCATION: Remote

ROLES & RESPONSIBILITIES:
- Lead the end-to-end development of customer-facing web applications using React / Next.js and Python backend APIs.
- Implement responsive, accessible UI designs with CSS modern frameworks and component libraries.
- Optimize database queries, API caching, and microservice architectures.
- Conduct code reviews, establish testing benchmarks, and mentor junior developers.

REQUIRED QUALIFICATIONS:
- 6+ years of full-stack web application development experience.
- Expert knowledge of TypeScript, React, HTML5/CSS3, and Python (FastAPI/Django).
- Proven track record leading developer teams and delivering scalable web platforms.
- Experience with CI/CD pipelines, Docker, and AWS cloud deployment.

NICE TO HAVE:
- Familiarity with AI/LLM API integrations in web frontends.
"""
}

SAMPLE_RESUMES: Dict[str, str] = {
    "Dr. Eleanor Vance (Strong Fit - Senior AI)": """
DR. ELEANOR VANCE
San Francisco, CA | eleanor.vance@ai-research-lab.io | linkedin.com/in/eleanor-vance-ai

EXECUTIVE SUMMARY:
Senior AI Architect and Computer Scientist with 7+ years of experience leading engineering teams in designing multi-agent LLM systems, self-correcting graphs, and enterprise AI automation tools. Expert in LangGraph, Python, Pydantic, and DeepSeek/OpenAI model fine-tuning.

WORK EXPERIENCE:
Lead AI Engineer | Apex Intelligence (2022 - Present)
- Designed and launched ApexAgent, an autonomous enterprise workflow platform built on LangGraph and Python 3.11, handling 15M daily requests.
- Engineered iterative reflection and evaluation loops that improved structured extraction accuracy from 74% to 96.8%.
- Integrated DeepSeek-Coder and OpenAI models with fallbacks, reducing API inference costs by 38%.
- Mentored a team of 6 AI engineers and published 3 internal whitepapers on agent state management.

Senior Machine Learning Engineer | NeuralScale Inc. (2019 - 2022)
- Developed RAG search pipelines using Qdrant vector DB and LangChain, enabling semantic document retrieval across 500,000 corporate resumes.
- Built custom Python REST APIs using FastAPI and Pydantic for automated candidate skill matching.

EDUCATION:
- Ph.D. in Computer Science (Focus: Artificial Intelligence & NLP), Stanford University (2019)
- B.S. in Computer Engineering, UC Berkeley (2015)

TECHNICAL SKILLS:
Languages: Python, TypeScript, SQL, Bash
AI Frameworks: LangGraph, LangChain, OpenAI API, DeepSeek API, PyTorch, Transformers, Pydantic
Tools & DBs: Docker, Kubernetes, Vector DBs (Qdrant, Pinecone), Git, Gradio, FastAPI
""",

    "Alex Mercer (Partial Fit - Mid Level Dev)": """
ALEX MERCER
Austin, TX | alex.mercer@devmail.com

SUMMARY:
Software Developer with 3.5 years of experience in Python web development, API integrations, and basic database management. Enthusiastic about artificial intelligence and modern Python frameworks.

EXPERIENCE:
Software Engineer | WebTech Solutions (2022 - Present)
- Built backend REST APIs in Python using Flask and Docker.
- Integrated third-party APIs including Stripe and SendGrid.
- Collaborated with frontend team to build simple internal dashboards using HTML, JavaScript, and Bootstrap.

Junior Python Developer | DataFlow LLC (2021 - 2022)
- Wrote web scrapers and ETL scripts to gather domain data.
- Maintained SQL database queries and unit test suites.

EDUCATION:
- B.S. in Computer Science, University of Texas at Austin (2021)

SKILLS:
Languages: Python, JavaScript, HTML/CSS, SQL
Frameworks: Flask, Django, REST APIs, Git, Docker
AI Knowledge: Completed online certificates in LangChain basics and Prompt Engineering.
""",

    "Jordan Lee (Weak Fit - Marketing Lead)": """
JORDAN LEE
Chicago, IL | jordan.lee@marketingpro.com

SUMMARY:
Results-driven Digital Marketing Director with 8+ years of experience driving brand awareness, recruitment marketing campaigns, and talent acquisition SEO strategies.

EXPERIENCE:
Marketing Lead | BrandForce (2020 - Present)
- Led talent acquisition marketing strategy, increasing applicant volume by 45%.
- Managed social media ad campaigns across LinkedIn and Glassdoor with a $200k quarterly budget.

EDUCATION:
- B.A. in Communications, Northwestern University
"""
}
