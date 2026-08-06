import gradio as gr
import json
import logging
from typing import Tuple, Dict, Any, List

from recruitment_agent.config import config
from recruitment_agent.utils import SAMPLE_JOB_DESCRIPTIONS, SAMPLE_RESUMES
from recruitment_agent.graph import build_recruitment_graph
from recruitment_agent.llm import get_llm
from recruitment_agent.sourcing_tools import SourcingTools, SourcedCandidate

logger = logging.getLogger(__name__)

# Pre-compile state graph
recruitment_app = build_recruitment_graph()

CSS = """
.container { max-width: 1200px; margin: 0 auto; }
.header-box {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
    color: white;
    padding: 24px;
    border-radius: 16px;
    margin-bottom: 20px;
    box-shadow: 0 10px 25px -5px rgba(67, 56, 202, 0.3);
}
.header-box h1 { color: #ffffff !important; font-size: 2.2rem; font-weight: 700; margin-bottom: 8px; }
.header-box p { color: #e0e7ff !important; font-size: 1.05rem; }
.card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 18px; margin-bottom: 15px; }
"""

# Global storage for fetched sourced candidates
SOURCED_CANDIDATES_CACHE: List[SourcedCandidate] = []

def load_preset(jd_key: str, resume_key: str) -> Tuple[str, str]:
    """Populates Job Description and Candidate Resume from sample presets."""
    jd_text = SAMPLE_JOB_DESCRIPTIONS.get(jd_key, "")
    resume_text = SAMPLE_RESUMES.get(resume_key, "")
    return jd_text, resume_text

def run_single_candidate_screening(
    jd_text: str,
    resume_text: str,
    required_exp: str,
    work_mode: str,
    target_location: str,
    api_key_input: str,
    model_choice: str
) -> Tuple[str, str, str, str, str]:
    """Executes the LangGraph recruitment graph for a single candidate with experience, work mode, and location filters."""
    if not jd_text.strip() or not resume_text.strip():
        return "⚠️ Please provide both a Job Description and Candidate Resume.", "", "", "", ""

    effective_api_key = api_key_input.strip() if api_key_input.strip() else config.DEEPSEEK_API_KEY

    initial_state = {
        "job_description": jd_text,
        "candidate_resume": resume_text,
        "required_experience": required_exp,
        "work_mode": work_mode,
        "target_location": target_location,
        "screening_report": None,
        "critique": None,
        "interview_kit": None,
        "reflection_count": 0,
        "execution_logs": [],
        "is_complete": False,
        "api_key": effective_api_key,
        "model_name": model_choice
    }

    try:
        final_state = recruitment_app.invoke(initial_state)
        
        screening = final_state.get("screening_report", {})
        critique = final_state.get("critique", {})
        interview_kit = final_state.get("interview_kit", {})
        logs = final_state.get("execution_logs", [])

        # Formatted Output 1: Match Score & Recommendation Badge
        name = screening.get("candidate_name", "Candidate")
        score = screening.get("overall_match_score", 0)
        rec = screening.get("recommendation", "N/A")
        
        status_md = f"### 👤 Candidate: **{name}**\n\n"
        status_md += f"🎯 **Overall Match Score:** `{score}%` &nbsp;&nbsp;|&nbsp;&nbsp; 📋 **Recommendation:** `{rec}`\n\n"
        status_md += f"**Executive Summary:** {screening.get('executive_summary', '')}\n\n"
        status_md += f"⏳ **Experience Fit:** {screening.get('experience_fit_commentary', 'N/A')}\n\n"
        status_md += f"📍 **Work Mode & Location Fit:** {screening.get('work_mode_and_location_fit', 'N/A')}\n\n"
        
        # Formatted Output 2: Key Qualifications & Dealbreakers
        qual_md = "#### ✅ Key Qualifications:\n" + "\n".join([f"- {q}" for q in screening.get("key_qualifications", [])])
        gaps_md = "\n\n#### ⚠️ Critical Gaps / Dealbreakers:\n" + "\n".join([f"- {g}" for g in screening.get("critical_gaps", [])])
        summary_md = qual_md + gaps_md

        # Formatted Output 3: Category Scores Breakdown
        cat_scores = screening.get("category_scores", [])
        cat_md = "### 📊 Dimension Breakdown\n\n"
        for cat in cat_scores:
            cat_md += f"**{cat.get('category')}** — Score: `{cat.get('score')}/100`\n"
            cat_md += f"*Commentary:* {cat.get('summary')}\n"
            if cat.get("strengths"):
                cat_md += f"- **Strengths:** {', '.join(cat.get('strengths'))}\n"
            if cat.get("gaps"):
                cat_md += f"- **Gaps:** {', '.join(cat.get('gaps'))}\n"
            cat_md += "\n---\n"

        # Formatted Output 4: LangGraph Execution & Reflection Loop Logs
        loop_md = "### 🔄 LangGraph Iterative Reflection Loop History\n\n"
        for entry in logs:
            loop_md += f"⏱️ `[{entry.get('timestamp')}]` **{entry.get('step_name')}** ({entry.get('node_id')})\n"
            loop_md += f"> {entry.get('detail')}\n\n"
            
        if critique:
            loop_md += f"**QA Audit Quality Score:** `{critique.get('quality_score')}/100`\n"
            loop_md += f"**Needs Refinement Loop:** `{critique.get('needs_revision')}`\n"
            if critique.get("critique_notes"):
                loop_md += "**Audit Critique Notes:**\n" + "\n".join([f"- {n}" for n in critique.get("critique_notes", [])])

        # Formatted Output 5: Interview Kit
        kit_md = ""
        if interview_kit:
            kit_md += f"### 🎙️ Interview Strategy & Kit for **{interview_kit.get('candidate_name', name)}**\n"
            kit_md += f"**Target Role Level:** `{interview_kit.get('suggested_role_level')}`\n\n"
            kit_md += f"**Primary Focus:** {interview_kit.get('interview_focus')}\n\n"
            kit_md += f"**Hiring Committee Advice:** {interview_kit.get('overall_hiring_advice')}\n\n"
            kit_md += "#### ❓ Targeted Interview Questions:\n\n"
            
            for idx, q in enumerate(interview_kit.get("questions", []), 1):
                kit_md += f"**{idx}. [{q.get('question_type')}] {q.get('topic')}**\n"
                kit_md += f"**Question:** *\"{q.get('question_text')}\"*\n\n"
                kit_md += f"📌 *Why Asked:* {q.get('why_asked')}\n"
                kit_md += f"💡 *Ideal Answer Rubric:* {q.get('ideal_answer_rubric')}\n\n---\n"

        return status_md, summary_md, cat_md, loop_md, kit_md

    except Exception as e:
        logger.error(f"Execution error in graph: {e}", exc_info=True)
        err_msg = f"❌ Error executing recruitment agent graph: {str(e)}"
        return err_msg, "", "", "", ""

def execute_sourcing_tool(
    source_tool: str,
    keywords: str,
    location_filter: str,
    local_path: str
) -> Tuple[str, List[List[Any]]]:
    """Invokes candidate sourcing tools across LinkedIn, Naukri, Indeed, Foundit, or Local Folder."""
    global SOURCED_CANDIDATES_CACHE
    SOURCED_CANDIDATES_CACHE.clear()

    if source_tool == "LinkedIn Recruiter Tool":
        SOURCED_CANDIDATES_CACHE = SourcingTools.fetch_from_linkedin(keywords, location_filter)
    elif source_tool == "Naukri India Tool":
        SOURCED_CANDIDATES_CACHE = SourcingTools.fetch_from_naukri(keywords, location=location_filter)
    elif source_tool == "Indeed Resume Tool":
        SOURCED_CANDIDATES_CACHE = SourcingTools.fetch_from_indeed(keywords, location_filter)
    elif source_tool == "Foundit (Monster India) Tool":
        SOURCED_CANDIDATES_CACHE = SourcingTools.fetch_from_foundit(keywords, location_filter)
    elif source_tool == "Local Folder Ingestion Tool":
        path = local_path.strip() if local_path.strip() else "."
        SOURCED_CANDIDATES_CACHE = SourcingTools.fetch_from_local_folder(path)
    
    table_rows = []
    for cand in SOURCED_CANDIDATES_CACHE:
        table_rows.append([
            cand.source_platform,
            cand.candidate_name,
            cand.current_title,
            cand.experience_years,
            cand.location,
            ", ".join(cand.key_skills)
        ])
        
    status = f"### 🔍 Sourced {len(table_rows)} candidate profile(s) via **{source_tool}**\nClick **'Import & Screen All Sourced Candidates'** to run them through the LangGraph AI Screener."
    return status, table_rows

def screen_sourced_candidates(
    jd_preset_key: str,
    required_exp: str,
    work_mode: str,
    target_location: str,
    api_key_input: str,
    model_choice: str
) -> Tuple[str, List[List[Any]]]:
    """Screens all candidates fetched from sourcing tools."""
    global SOURCED_CANDIDATES_CACHE
    if not SOURCED_CANDIDATES_CACHE:
        return "⚠️ No sourced candidates in cache. Please run a sourcing tool search first.", []

    jd_text = SAMPLE_JOB_DESCRIPTIONS.get(jd_preset_key, "")
    effective_api_key = api_key_input.strip() if api_key_input.strip() else config.DEEPSEEK_API_KEY
    
    results = []
    for cand in SOURCED_CANDIDATES_CACHE:
        state = {
            "job_description": jd_text,
            "candidate_resume": cand.raw_resume_text,
            "required_experience": required_exp,
            "work_mode": work_mode,
            "target_location": target_location,
            "screening_report": None,
            "critique": None,
            "interview_kit": None,
            "reflection_count": 0,
            "execution_logs": [],
            "is_complete": False,
            "api_key": effective_api_key,
            "model_name": model_choice
        }
        final_state = recruitment_app.invoke(state)
        report = final_state.get("screening_report", {})
        
        results.append([
            cand.source_platform,
            cand.candidate_name,
            f"{report.get('overall_match_score', 0)}%",
            report.get("recommendation", "N/A"),
            report.get("experience_fit_commentary", "N/A")[:50] + "...",
            report.get("work_mode_and_location_fit", "N/A")[:50] + "..."
        ])
        
    results.sort(key=lambda x: int(x[2].replace("%", "")), reverse=True)
    summary = f"### 🏆 Screening Leaderboard for {len(results)} Sourced Candidate(s)\nCriteria: Experience=`{required_exp}`, WorkMode=`{work_mode}`, Location=`{target_location}`"
    return summary, results

def run_batch_candidate_leaderboard(
    jd_key: str,
    required_exp: str,
    work_mode: str,
    target_location: str,
    api_key_input: str,
    model_choice: str
) -> Tuple[str, List[List[Any]]]:
    """Runs screening across all sample resumes to generate a comparison leaderboard."""
    jd_text = SAMPLE_JOB_DESCRIPTIONS.get(jd_key, "")
    effective_api_key = api_key_input.strip() if api_key_input.strip() else config.DEEPSEEK_API_KEY

    results = []
    
    for r_name, r_text in SAMPLE_RESUMES.items():
        state = {
            "job_description": jd_text,
            "candidate_resume": r_text,
            "required_experience": required_exp,
            "work_mode": work_mode,
            "target_location": target_location,
            "screening_report": None,
            "critique": None,
            "interview_kit": None,
            "reflection_count": 0,
            "execution_logs": [],
            "is_complete": False,
            "api_key": effective_api_key,
            "model_name": model_choice
        }
        res_state = recruitment_app.invoke(state)
        report = res_state.get("screening_report", {})
        
        results.append([
            report.get("candidate_name", r_name.split("(")[0].strip()),
            f"{report.get('overall_match_score', 0)}%",
            report.get("recommendation", "N/A"),
            ", ".join(report.get("key_qualifications", [])[:2]),
            ", ".join(report.get("critical_gaps", [])[:2])
        ])
        
    results.sort(key=lambda x: int(x[1].replace("%", "")), reverse=True)
    
    summary = f"### 🏆 Candidate Leaderboard for `{jd_key}`\nCriteria: Experience=`{required_exp}`, Work Mode=`{work_mode}`, Location=`{target_location}`"
    return summary, results

def test_api_connection(api_key: str, base_url: str, model: str) -> str:
    """Tests connection to DeepSeek API endpoint."""
    key = api_key.strip() if api_key.strip() else config.DEEPSEEK_API_KEY
    if not key:
        return "⚠️ No DeepSeek API Key provided. Application will continue in Mock Mode."
    
    try:
        llm = get_llm(api_key=key, base_url=base_url, model_name=model)
        res = llm.invoke("Respond with 'OK' if you receive this message.")
        return f"✅ Successfully connected to DeepSeek API ({model})! Response: {res.content.strip()}"
    except Exception as e:
        return f"❌ Connection test failed: {str(e)}"

def create_ui() -> gr.Blocks:
    """Constructs the Gradio interface."""
    with gr.Blocks() as demo:
        
        # Header Box
        with gr.Row(elem_classes=["header-box"]):
            with gr.Column():
                gr.Markdown(
                    "# 🤖 Recruitment & Selection AI Agent\n"
                    "**Automated Candidate Sourcing, Experience & Work Mode Filtering, Reflection Loops, & Interview Kits**\n"
                    "*Powered by LangGraph, Python, Gradio, and DeepSeek API*"
                )

        with gr.Tabs():
            # TAB 1: Single Candidate Screener
            with gr.TabItem("🔍 Single Candidate Screening & Loop Inspector"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📥 Select Preset or Custom Input")
                        jd_preset = gr.Dropdown(
                            choices=list(SAMPLE_JOB_DESCRIPTIONS.keys()),
                            value="Senior AI & LangGraph Engineer",
                            label="Sample Job Description Preset"
                        )
                        resume_preset = gr.Dropdown(
                            choices=list(SAMPLE_RESUMES.keys()),
                            value="Dr. Eleanor Vance (Strong Fit - Senior AI)",
                            label="Sample Candidate Resume Preset"
                        )
                        btn_load = gr.Button("📋 Load Preset into Fields", variant="secondary")

                        gr.Markdown("### ⚙️ Screening Criteria & Work Mode Filters")
                        with gr.Row():
                            required_exp_in = gr.Dropdown(
                                choices=["0-2 Years (Junior)", "2-5 Years (Mid)", "5-8 Years (Senior)", "8+ Years (Lead / Principal)", "Flexible"],
                                value="5-8 Years (Senior)",
                                label="Required Experience Level"
                            )
                            work_mode_in = gr.Radio(
                                choices=["Remote", "Work From Office", "Hybrid", "Any / Flexible"],
                                value="Remote",
                                label="Preferred Work Mode"
                            )
                        
                        target_location_in = gr.Textbox(
                            label="Target Location",
                            value="San Francisco, CA / Remote",
                            placeholder="e.g. Bengaluru, San Francisco, New York..."
                        )
                        
                        jd_input = gr.Textbox(
                            label="Job Description",
                            lines=7,
                            placeholder="Paste full Job Description requirements..."
                        )
                        resume_input = gr.Textbox(
                            label="Candidate Resume",
                            lines=8,
                            placeholder="Paste candidate resume text..."
                        )
                        btn_run = gr.Button("🚀 Run AI Recruitment Graph", variant="primary", size="lg")

                    with gr.Column(scale=1):
                        gr.Markdown("### 🎯 Screening Results & Reflection Logs")
                        status_out = gr.Markdown(label="Match & Recommendation")
                        summary_out = gr.Markdown(label="Qualifications & Gaps")
                        cat_out = gr.Markdown(label="Dimension Scoring")
                        loop_out = gr.Markdown(label="LangGraph Reflection Loops")

            # TAB 2: Candidate Sourcing Tools (LinkedIn, Naukri, Indeed, Foundit, Local Folder)
            with gr.TabItem("🌐 Candidate Sourcing Tools"):
                gr.Markdown("### Sourcing & Ingestion Tools (LinkedIn, Naukri, Indeed, Foundit, Local Disk Directory)")
                with gr.Row():
                    sourcing_tool_select = gr.Dropdown(
                        choices=[
                            "LinkedIn Recruiter Tool",
                            "Naukri India Tool",
                            "Indeed Resume Tool",
                            "Foundit (Monster India) Tool",
                            "Local Folder Ingestion Tool"
                        ],
                        value="LinkedIn Recruiter Tool",
                        label="Select Sourcing / Import Tool"
                    )
                    search_keywords = gr.Textbox(
                        label="Job Keywords / Title",
                        value="Senior AI LangGraph Engineer"
                    )
                    location_filter = gr.Textbox(
                        label="Location Filter",
                        value="Remote"
                    )
                
                with gr.Row():
                    local_folder_path = gr.Textbox(
                        label="Local Folder Path (For Local Folder Ingestion Tool)",
                        placeholder="e.g. C:\\Users\\Lenovo\\Desktop\\Sangeetha--Agent--1 or relative path",
                        value="."
                    )
                    btn_run_sourcing = gr.Button("🔍 Fetch Candidates via Tool", variant="primary")

                sourced_status_out = gr.Markdown()
                sourced_table = gr.Dataframe(
                    headers=["Platform", "Candidate Name", "Current Title", "Experience", "Location", "Key Skills"],
                    datatype=["str", "str", "str", "str", "str", "str"],
                    label="Sourced Profiles"
                )

                gr.Markdown("---")
                gr.Markdown("### ⚡ Screening & Evaluating Sourced Candidates")
                with gr.Row():
                    sourcing_target_jd = gr.Dropdown(
                        choices=list(SAMPLE_JOB_DESCRIPTIONS.keys()),
                        value="Senior AI & LangGraph Engineer",
                        label="Target Job Description for Screening"
                    )
                    sourcing_exp = gr.Dropdown(
                        choices=["0-2 Years", "2-5 Years", "5-8 Years", "8+ Years", "Flexible"],
                        value="5-8 Years",
                        label="Min Required Experience"
                    )
                    sourcing_work_mode = gr.Radio(
                        choices=["Remote", "Work From Office", "Hybrid", "Any"],
                        value="Remote",
                        label="Work Mode"
                    )
                
                btn_screen_sourced = gr.Button("⚡ Import & Screen All Sourced Candidates", variant="primary", size="lg")

                sourced_screening_status = gr.Markdown()
                sourced_screening_table = gr.Dataframe(
                    headers=["Source", "Candidate Name", "Match Score", "Recommendation", "Experience Fit", "Work Mode & Location Fit"],
                    datatype=["str", "str", "str", "str", "str", "str"],
                    label="Sourced Candidates Evaluation Leaderboard"
                )

            # TAB 3: Candidate Leaderboard
            with gr.TabItem("🏆 Multi-Candidate Leaderboard"):
                gr.Markdown("### Compare Multiple Candidates Side-by-Side Against a Single Job Description")
                with gr.Row():
                    lead_jd_preset = gr.Dropdown(
                        choices=list(SAMPLE_JOB_DESCRIPTIONS.keys()),
                        value="Senior AI & LangGraph Engineer",
                        label="Target Job Description"
                    )
                    lead_exp = gr.Dropdown(
                        choices=["0-2 Years", "2-5 Years", "5-8 Years", "8+ Years", "Flexible"],
                        value="5-8 Years",
                        label="Required Experience"
                    )
                    lead_work_mode = gr.Radio(
                        choices=["Remote", "Work From Office", "Hybrid", "Any"],
                        value="Remote",
                        label="Work Mode"
                    )
                    btn_run_leaderboard = gr.Button("⚡ Screen All Batch Candidates", variant="primary")
                
                lead_summary = gr.Markdown()
                leaderboard_table = gr.Dataframe(
                    headers=["Candidate Name", "Match Score", "Recommendation", "Top Qualifications", "Key Gaps"],
                    datatype=["str", "str", "str", "str", "str"],
                    label="Candidate Rankings"
                )

            # TAB 4: Interview Kit Generator
            with gr.TabItem("🎙️ AI Interview Kit"):
                gr.Markdown("### Customized Role-Specific Interview Questions & Rubrics")
                interview_kit_out = gr.Markdown(value="*Run candidate screening in Tab 1 to automatically generate the custom interview kit here.*")

            # TAB 5: DeepSeek API & Settings
            with gr.TabItem("⚙️ DeepSeek Settings & API Setup"):
                gr.Markdown("### DeepSeek API Configuration & LangGraph Settings")
                with gr.Row():
                    api_key_in = gr.Textbox(
                        label="DeepSeek API Key",
                        type="password",
                        placeholder="sk-...",
                        value=config.DEEPSEEK_API_KEY
                    )
                    base_url_in = gr.Textbox(
                        label="DeepSeek Base URL",
                        value=config.DEEPSEEK_BASE_URL
                    )
                    model_in = gr.Dropdown(
                        choices=["deepseek-chat", "deepseek-reasoner"],
                        value=config.DEEPSEEK_MODEL,
                        label="DeepSeek Model"
                    )
                btn_test_api = gr.Button("🔌 Test API Connection")
                api_status = gr.Markdown()

        # Wire Event Handlers
        btn_load.click(
            fn=load_preset,
            inputs=[jd_preset, resume_preset],
            outputs=[jd_input, resume_input]
        )
        
        demo.load(
            fn=load_preset,
            inputs=[jd_preset, resume_preset],
            outputs=[jd_input, resume_input]
        )

        btn_run.click(
            fn=run_single_candidate_screening,
            inputs=[jd_input, resume_input, required_exp_in, work_mode_in, target_location_in, api_key_in, model_in],
            outputs=[status_out, summary_out, cat_out, loop_out, interview_kit_out]
        )

        btn_run_sourcing.click(
            fn=execute_sourcing_tool,
            inputs=[sourcing_tool_select, search_keywords, location_filter, local_folder_path],
            outputs=[sourced_status_out, sourced_table]
        )

        btn_screen_sourced.click(
            fn=screen_sourced_candidates,
            inputs=[sourcing_target_jd, sourcing_exp, sourcing_work_mode, location_filter, api_key_in, model_in],
            outputs=[sourced_screening_status, sourced_screening_table]
        )

        btn_run_leaderboard.click(
            fn=run_batch_candidate_leaderboard,
            inputs=[lead_jd_preset, lead_exp, lead_work_mode, target_location_in, api_key_in, model_in],
            outputs=[lead_summary, leaderboard_table]
        )

        btn_test_api.click(
            fn=test_api_connection,
            inputs=[api_key_in, base_url_in, model_in],
            outputs=[api_status]
        )

    return demo
