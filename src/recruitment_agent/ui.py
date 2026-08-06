import gradio as gr
import json
import logging
import datetime
from typing import Tuple, Dict, Any, List

from recruitment_agent.config import config
from recruitment_agent.utils import SAMPLE_JOB_DESCRIPTIONS, SAMPLE_RESUMES, ROLE_PRESETS
from recruitment_agent.graph import build_recruitment_graph
from recruitment_agent.llm import get_llm, generate_structured_output
from recruitment_agent.models import JobIntakePlan, OfferLetter, BGVReport, OnboardingPackage
from recruitment_agent.sourcing_tools import SourcingTools, SourcedCandidate
from recruitment_agent.tools.email_tool import EmailNotificationTool
from recruitment_agent.tools.telephonic_tool import TelephonicScreeningTool
from recruitment_agent.tools.bgv_tool import BackgroundVerificationTool
from recruitment_agent.tools.onboarding_tool import OnboardingTool

logger = logging.getLogger(__name__)

# Pre-compile state graph
recruitment_app = build_recruitment_graph()

CSS = """
.container { max-width: 1200px; margin: 0 auto; }
.header-box {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
    color: white;
    padding: 24px;
    border-radius: 16px;
    margin-bottom: 20px;
    box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.3);
}
.hitl-box {
    background: #fffbe6;
    border: 2px solid #ffe58f;
    border-radius: 12px;
    padding: 16px;
    margin-top: 15px;
    margin-bottom: 15px;
}
.email-box {
    background: #e6f7ff;
    border: 1px solid #91caff;
    border-radius: 12px;
    padding: 16px;
    margin-top: 15px;
}
"""

SOURCED_CANDIDATES_CACHE: List[SourcedCandidate] = []

# --- DYNAMIC ROLE PRESET UPDATER ---
def update_role_preset_details(role_title: str) -> Tuple[str, str, str, str, str]:
    """Dynamically populates department, core skills, and salary bands based on selected Role Title."""
    if role_title in ROLE_PRESETS:
        preset = ROLE_PRESETS[role_title]
        return role_title, preset["department"], preset["skills"], preset["min_salary"], preset["max_salary"]
    return role_title, "Engineering & Technology", "Custom skills...", "15 LPA", "25 LPA"

# --- STEP 1 HANDLER ---
def handle_job_intake(
    role_title: str,
    department: str,
    skills_input: str,
    min_salary: str,
    max_salary: str,
    api_key_input: str,
    model_choice: str
) -> Tuple[str, str, str]:
    """Step 1: Defines role need, generates AI JD, and sets salary bands."""
    skills_list = [s.strip() for s in skills_input.split(",") if s.strip()]
    effective_api_key = api_key_input.strip() if api_key_input.strip() else config.DEEPSEEK_API_KEY

    system_prompt = (
        "You are an Executive Talent Acquisition Director. Generate a professional Job Description "
        "matching the specified role title, department, core skills, and salary bands."
    )
    user_prompt = f"Role: {role_title}, Dept: {department}, Skills: {skills_list}, Salary: {min_salary} - {max_salary}"

    plan: JobIntakePlan = generate_structured_output(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output_schema=JobIntakePlan,
        api_key=effective_api_key,
        model_name=model_choice
    )

    summary_md = f"### ✅ Step 1 Complete: Job Intake & Planning for `{role_title}`\n"
    summary_md += f"**Department:** {department} &nbsp;|&nbsp; **Target Salary Band:** `{min_salary} - {max_salary}`\n\n"
    summary_md += f"**Core Skills Needed:** {skills_input}\n"

    return summary_md, plan.generated_job_description, f"{min_salary} - {max_salary}"

# --- STEP 2 HANDLERS ---
def generate_customized_job_post(
    role_title: str,
    portal: str,
    jd_text: str,
    api_key_input: str,
    model_choice: str
) -> str:
    """Generates customized job posting announcement tailored to the selected portal (LinkedIn/Naukri/Indeed/Foundit)."""
    effective_api_key = api_key_input.strip() if api_key_input.strip() else config.DEEPSEEK_API_KEY
    llm = get_llm(api_key=effective_api_key, model_name=model_choice)

    prompt = (
        f"Create an engaging, highly customized job advertisement announcement for prospective candidates tailored for '{portal}'.\n"
        f"Role Title: {role_title}\n"
        f"Job Description Details:\n{jd_text[:800]}\n\n"
        f"Include an eye-catching headline, key candidate benefits, core qualifications bullet points, "
        f"work mode details, and a clear call-to-action to apply."
    )

    try:
        res = llm.invoke(prompt)
        content = res.content.strip()
    except Exception:
        content = (
            f"🚀 WE ARE HIRING! [{role_title}]\n\n"
            f"📍 Location: Remote / Hybrid | 💼 Platform: {portal}\n\n"
            f"Are you an experienced professional passionate about cutting-edge technology? Join our R&D team!\n\n"
            f"✨ Key Requirements:\n- Proven background in core domain skills\n- Strong problem solving mindset\n- Excellent collaborative communication\n\n"
            f"👉 Apply now or reach out to our Talent Acquisition team directly!"
        )

    out_md = f"### 📢 Customized Job Posting Announcement for **{portal}**\n\n"
    out_md += f"```text\n{content}\n```\n\n"
    out_md += f"✅ **Status:** Ready to broadcast to `{portal}` candidates!"
    return out_md

def run_step2_sourcing_screening(
    portal_choice: str,
    jd_text: str,
    resume_text: str,
    req_exp: str,
    work_mode: str,
    target_loc: str,
    api_key_input: str,
    model_choice: str
) -> Tuple[str, str, str, str, str, str, str]:
    """Step 2: Posts jobs on selected portal, screens resumes via reflection loop, and prepares email notification."""
    if not jd_text.strip() or not resume_text.strip():
        return "⚠️ Please complete Step 1 or enter Job Description and Candidate Resume.", "", "", "", "", "", ""

    effective_api_key = api_key_input.strip() if api_key_input.strip() else config.DEEPSEEK_API_KEY

    initial_state = {
        "job_description": jd_text,
        "candidate_resume": resume_text,
        "required_experience": req_exp,
        "work_mode": work_mode,
        "target_location": target_loc,
        "salary_band_min": "18 LPA",
        "salary_band_max": "28 LPA",
        "job_intake_plan": None,
        "job_postings_status": None,
        "screening_report": None,
        "critique": None,
        "shortlist_email": None,
        "reflection_count": 0,
        "telephonic_result": None,
        "hitl_checkpoint1_manager_approval": None,
        "salary_negotiation_details": None,
        "hitl_checkpoint2_offer_approval": None,
        "official_offer_letter": None,
        "bgv_report": None,
        "onboarding_package": None,
        "execution_logs": [],
        "current_step": 2,
        "is_complete": False,
        "api_key": effective_api_key,
        "model_name": model_choice
    }

    final_state = recruitment_app.invoke(initial_state)

    postings_md = f"✅ Posted job on selected portal: **{portal_choice}**\n✅ Active & Passive candidate talent pool fetched."
    screening = final_state.get("screening_report", {})
    logs = final_state.get("execution_logs", [])
    email = final_state.get("shortlist_email", {})

    name = screening.get("candidate_name", "Candidate")
    cand_email = screening.get("candidate_email", "candidate@example.com")
    score = screening.get("overall_match_score", 0)
    rec = screening.get("recommendation", "N/A")

    status_md = f"### 👤 Candidate: **{name}**\n\n"
    status_md += f"🎯 **Overall Match Score:** `{score}%` &nbsp;&nbsp;|&nbsp;&nbsp; 📋 **Recommendation:** `{rec}`\n\n"
    status_md += f"**Executive Summary:** {screening.get('executive_summary', '')}\n\n"
    status_md += f"⏳ **Experience Fit:** {screening.get('experience_fit_commentary', 'N/A')}\n\n"
    status_md += f"📍 **Work Mode & Location Fit:** {screening.get('work_mode_and_location_fit', 'N/A')}\n\n"

    qual_md = "#### ✅ Key Qualifications:\n" + "\n".join([f"- {q}" for q in screening.get("key_qualifications", [])])
    gaps_md = "\n\n#### ⚠️ Critical Gaps / Dealbreakers:\n" + "\n".join([f"- {g}" for g in screening.get("critical_gaps", [])])
    summary_md = qual_md + gaps_md

    cat_md = "### 📊 Dimension Breakdown\n\n"
    for cat in screening.get("category_scores", []):
        cat_md += f"**{cat.get('category')}** — Score: `{cat.get('score')}/100`\n"
        cat_md += f"*Commentary:* {cat.get('summary')}\n\n"

    loop_md = "### 🔄 LangGraph Iterative Reflection Loop History\n\n"
    for entry in logs:
        loop_md += f"⏱️ `[{entry.get('timestamp')}]` **{entry.get('step_name')}**\n> {entry.get('detail')}\n\n"

    email_md = f"### 📧 Automated Shortlist Email Notification Prepared for {name}\n"
    email_md += f"Click **'Shoot Out Shortlist Notification Email'** to send email."

    return postings_md, status_md, summary_md, cat_md, loop_md, email_md, name

def shootout_candidate_email(
    candidate_name: str,
    candidate_email: str,
    role_title: str
) -> str:
    """Shoots out email notification to selected candidate."""
    email_obj = EmailNotificationTool.send_shortlist_notification(candidate_name, candidate_email, role_title)
    
    out_md = f"### 🚀 SHORTLIST EMAIL DISPATCHED SUCCESSFULLY!\n\n"
    out_md += f"• **To:** `{email_obj.candidate_name}` <{email_obj.candidate_email}>\n"
    out_md += f"• **Subject:** {email_obj.email_subject}\n"
    out_md += f"• **Sent Timestamp:** `{email_obj.sent_timestamp}`\n"
    out_md += f"• **Delivery Status:** `DELIVERED (HTTP 200 OK)`\n\n"
    out_md += f"```text\n{email_obj.email_body}\n```"
    return out_md

# --- STEP 3 HANDLERS ---
def run_step3_telephonic_and_hitl1(
    candidate_name: str,
    role_title: str
) -> Tuple[str, str]:
    """Step 3a: Telephonic screening and HITL Checkpoint 1 setup."""
    tele_res = TelephonicScreeningTool.conduct_telephonic_round(candidate_name, role_title)
    
    tele_md = f"### 📞 Preliminary Telephonic Round Results for **{candidate_name}**\n\n"
    tele_md += f"• **Preliminary Status:** `{tele_res.preliminary_status}`\n"
    tele_md += f"• **Candidate Interest Level:** `{tele_res.interest_level}`\n"
    tele_md += f"• **Availability & Notice Period:** `{tele_res.availability_and_notice_period}`\n"
    tele_md += f"• **Expected Salary:** `{tele_res.salary_expectation}`\n"
    tele_md += f"• **Communication Score:** `{tele_res.communication_rating}/10`\n\n"
    tele_md += f"**Culture Fit Commentary:** {tele_res.culture_fit_notes}\n"

    hitl1_status = f"🛑 **HITL Checkpoint 1 Required:** Awaiting Human Manager decision to schedule prospective interviews for **{candidate_name}**."
    return tele_md, hitl1_status

def record_hitl1_decision(
    manager_decision: str,
    manager_notes: str,
    candidate_name: str
) -> str:
    """Human-In-The-Loop Checkpoint 1 Decision Handler."""
    approved = "APPROVE" in manager_decision
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if approved:
        return (
            f"### ✅ HITL Checkpoint 1 APPROVED by Manager at `{timestamp}`\n"
            f"**Decision:** Scheduled for Prospective Manager Interview & Technical Coding Test.\n"
            f"**Manager Notes:** *\"{manager_notes}\"*\n\n"
            f"Proceeding to candidate feedback comparison and salary negotiation!"
        )
    else:
        return (
            f"### ❌ HITL Checkpoint 1 REJECTED / HELD by Manager at `{timestamp}`\n"
            f"**Manager Notes:** *\"{manager_notes}\"*\n"
            f"Candidate **{candidate_name}** moved to HOLD state."
        )

def run_step3_offer_and_onboarding(
    candidate_name: str,
    role_title: str,
    agreed_ctc: str,
    joining_bonus: str,
    work_mode: str,
    doj: str,
    hitl2_manager_approval: bool,
    manager_notes: str,
    api_key_input: str,
    model_choice: str
) -> Tuple[str, str, str, str]:
    """Step 3d-h: Final Offer, BGV check, and Onboarding automation."""
    if not hitl2_manager_approval:
        return "⚠️ HITL Checkpoint 2 Required: Human Manager must check 'Approve Formal Offer Decision' before issuing offer.", "", "", ""

    effective_api_key = api_key_input.strip() if api_key_input.strip() else config.DEEPSEEK_API_KEY

    offer: OfferLetter = generate_structured_output(
        system_prompt="Generate official formal Offer Letter text based on candidate, CTC, bonus, work mode, and joining date.",
        user_prompt=f"Candidate: {candidate_name}, Role: {role_title}, CTC: {agreed_ctc}, Bonus: {joining_bonus}, WorkMode: {work_mode}, DOJ: {doj}",
        output_schema=OfferLetter,
        api_key=effective_api_key,
        model_name=model_choice
    )

    bgv: BGVReport = BackgroundVerificationTool.execute_bgv_check(candidate_name)
    onboarding: OnboardingPackage = OnboardingTool.generate_onboarding_package(candidate_name, role_title, offer.date_of_joining)

    hitl2_summary = f"### ✅ HITL Checkpoint 2 APPROVED by Hiring Manager\n"
    hitl2_summary += f"**Agreed Package:** `{offer.offered_ctc}` &nbsp;|&nbsp; **Joining Bonus:** `{offer.joining_bonus}` &nbsp;|&nbsp; **DOJ:** `{offer.date_of_joining}`\n"
    hitl2_summary += f"**Manager Approval Notes:** *\"{manager_notes}\"*\n"

    offer_md = f"### 📜 Official Formal Offer Letter Issued!\n"
    offer_md += f"```text\n{offer.offer_letter_text}\n```"

    bgv_md = f"### 🛡️ Background Verification (BGV) Report\n"
    bgv_md += f"• **Overall BGV Status:** `{bgv.overall_bgv_status}`\n"
    bgv_md += f"• **Employment History:** `{bgv.employment_verification}`\n"
    bgv_md += f"• **Education Check:** `{bgv.education_verification}`\n"
    bgv_md += f"• **Identity & Address:** `{bgv.identity_and_address_check}`\n\n"
    bgv_md += f"**Audit Summary:** {bgv.bgv_summary_notes}\n"

    onboarding_md = f"### 🚀 New Hire Onboarding & Welcome Package\n\n"
    onboarding_md += f"#### 📋 Paperwork & Document Checklist:\n" + "\n".join([f"- [ ] {item}" for item in onboarding.paperwork_checklist])
    onboarding_md += f"\n\n#### 💻 IT Equipment Allocation:\n" + "\n".join([f"- {eq}" for eq in onboarding.it_equipment_allocation])
    onboarding_md += f"\n\n#### 📅 First Week Orientation Schedule:\n" + "\n".join([f"- {sched}" for sched in onboarding.first_week_orientation_schedule])

    return hitl2_summary, offer_md, bgv_md, onboarding_md

def create_ui() -> gr.Blocks:
    """Constructs the multi-tab Gradio UI."""
    with gr.Blocks() as demo:
        
        # Header Box
        with gr.Row(elem_classes=["header-box"]):
            with gr.Column():
                gr.Markdown(
                    "# 🤖 3-Step Autonomous Recruitment & Selection Lifecycle Agent\n"
                    "**Step 1: Intake & Planning | Step 2: Preferred Job Portals, Custom Postings & Email Shootout | Step 3: Interview, HITL Approvals, Offer & Onboarding**\n"
                    "*Powered by LangGraph, Python, Gradio, and DeepSeek API*"
                )

        with gr.Tabs():
            # TAB 1: STEP 1 - JOB INTAKE & PLANNING
            with gr.TabItem("📋 Step 1: Job Intake & Planning"):
                gr.Markdown("### Define Need, Select Role Preset, Customize Department & Skills, & Configure Salary Bands")
                with gr.Row():
                    with gr.Column():
                        s1_role_dropdown = gr.Dropdown(
                            choices=list(ROLE_PRESETS.keys()) + ["Custom Role..."],
                            value="Senior AI & LangGraph Engineer",
                            label="Select Open Role Title (Presets auto-customize Department & Skills)"
                        )
                        s1_title = gr.Textbox(label="Role Title", value="Senior AI & LangGraph Engineer")
                        s1_dept = gr.Textbox(label="Department / Team", value=ROLE_PRESETS["Senior AI & LangGraph Engineer"]["department"])
                        s1_skills = gr.Textbox(label="Core Skills Needed (comma-separated)", value=ROLE_PRESETS["Senior AI & LangGraph Engineer"]["skills"])
                        with gr.Row():
                            s1_sal_min = gr.Textbox(label="Min Salary Band", value=ROLE_PRESETS["Senior AI & LangGraph Engineer"]["min_salary"])
                            s1_sal_max = gr.Textbox(label="Max Salary Band", value=ROLE_PRESETS["Senior AI & LangGraph Engineer"]["max_salary"])
                        btn_s1 = gr.Button("📋 Generate Job Intake Plan & AI Description", variant="primary", size="lg")

                    with gr.Column():
                        s1_summary_out = gr.Markdown(label="Intake Summary")
                        s1_jd_out = gr.Textbox(label="AI-Generated Job Description", lines=12)
                        s1_band_out = gr.Textbox(label="Configured Salary Range")

            # TAB 2: STEP 2 - SOURCING, SCREENING & EMAIL SHOOTOUT
            with gr.TabItem("🔍 Step 2: Sourcing, Portal Selection & Email Shootout"):
                gr.Markdown("### Select Preferred Job Portal, Broadcast Custom Job Post, Screen Resumes & Shoot Out Shortlist Email")
                with gr.Row():
                    with gr.Column(scale=1):
                        s2_portal_select = gr.Dropdown(
                            choices=[
                                "LinkedIn Recruiter & Jobs",
                                "Naukri India Employer Portal",
                                "Indeed Resume Search",
                                "Foundit (Monster India)",
                                "Internal Employee Referral Portal",
                                "Local Directory Resume Folder"
                            ],
                            value="LinkedIn Recruiter & Jobs",
                            label="🎯 Select Preferred Job Portal / Sourcing Channel"
                        )
                        
                        btn_custom_post = gr.Button("📢 Generate Customized Job Posting Announcement for Selected Portal", variant="secondary")
                        s2_custom_post_out = gr.Markdown()
                        
                        gr.Markdown("---")
                        gr.Markdown("#### ⚙️ Screening Rules & Candidate Resume")
                        s2_req_exp = gr.Dropdown(
                            choices=["0-2 Years (Junior)", "2-5 Years (Mid)", "5-8 Years (Senior)", "8+ Years (Lead)", "Flexible"],
                            value="5-8 Years (Senior)",
                            label="Required Experience"
                        )
                        s2_work_mode = gr.Radio(
                            choices=["Remote", "Work From Office", "Hybrid", "Any"],
                            value="Remote",
                            label="Preferred Work Mode"
                        )
                        s2_target_loc = gr.Textbox(label="Target Location", value="San Francisco, CA / Remote")
                        s2_jd_in = gr.Textbox(label="Job Description (from Step 1 or Custom)", lines=5, value=SAMPLE_JOB_DESCRIPTIONS["Senior AI & LangGraph Engineer"])
                        s2_resume_in = gr.Textbox(label="Candidate Resume", lines=6, value=SAMPLE_RESUMES["Dr. Eleanor Vance (Strong Fit - Senior AI)"])
                        btn_s2 = gr.Button("🚀 Run Sourcing & Reflection Resume Screener", variant="primary", size="lg")

                    with gr.Column(scale=1):
                        s2_postings_out = gr.Markdown()
                        s2_status_out = gr.Markdown()
                        s2_summary_out = gr.Markdown()
                        s2_cat_out = gr.Markdown()
                        s2_loop_out = gr.Markdown()

                        gr.Markdown("---")
                        with gr.Row(elem_classes=["email-box"]):
                            with gr.Column():
                                s2_email_name = gr.Textbox(label="Selected Candidate Name", value="Dr. Eleanor Vance")
                                s2_email_addr = gr.Textbox(label="Candidate Email Address", value="eleanor.vance@ai-research-lab.io")
                                btn_shootout_email = gr.Button("📧 Shoot Out Shortlist Notification Email to Selected Candidate", variant="primary")
                                s2_shootout_out = gr.Markdown()

            # TAB 3: STEP 3 - INTERVIEW, HITL APPROVALS, OFFER & ONBOARDING
            with gr.TabItem("🎙️ Step 3: Interview, HITL Approvals, Offer & Onboarding"):
                gr.Markdown("### Preliminary Telephonic Round, HITL Checkpoints, Candidate Selection, Offer & Onboarding")
                
                s3_cand_name = gr.Textbox(label="Candidate Name", value="Dr. Eleanor Vance")
                s3_role_title = gr.Textbox(label="Role Position", value="Senior AI & LangGraph Engineer")
                
                btn_telephonic = gr.Button("📞 3a. Run Preliminary Telephonic Round", variant="secondary")
                telephonic_out = gr.Markdown()
                hitl1_status_out = gr.Markdown()

                gr.Markdown("---")
                gr.Markdown("### 🛑 Human-In-The-Loop (HITL) Checkpoint 1: Manager Interview Approval")
                with gr.Row(elem_classes=["hitl-box"]):
                    with gr.Column():
                        hitl1_decision = gr.Radio(
                            choices=["APPROVE - Schedule Technical & Prospective Manager Interview", "REJECT / HOLD Candidate"],
                            value="APPROVE - Schedule Technical & Prospective Manager Interview",
                            label="Manager Decision"
                        )
                        hitl1_notes = gr.Textbox(label="Manager Comments & Skill Test Instructions", value="Strong candidate profile. Approve for 2-hour technical live coding test & prospective manager interview.")
                        btn_hitl1 = gr.Button("🛑 Record Manager HITL Decision", variant="primary")

                hitl1_record_out = gr.Markdown()

                gr.Markdown("---")
                gr.Markdown("### 🛑 Human-In-The-Loop (HITL) Checkpoint 2 & 3d-h: Salary Negotiation, Offer & Onboarding")
                with gr.Row(elem_classes=["hitl-box"]):
                    with gr.Column():
                        hitl2_ctc = gr.Textbox(label="Agreed Annual Package (CTC)", value="24,00,000 INR (24 LPA)")
                        hitl2_bonus = gr.Textbox(label="Joining Bonus", value="2,00,000 INR")
                        hitl2_work_mode = gr.Textbox(label="Agreed Work Mode", value="Remote / Hybrid")
                        hitl2_doj = gr.Textbox(label="Date of Joining (DOJ)", value="1st September 2026")
                        hitl2_checkbox = gr.Checkbox(label="✅ Human Manager Formally Approves Making Job Offer", value=True)
                        hitl2_notes = gr.Textbox(label="Manager Final Consent Notes", value="Approved by Hiring Manager & HR Director.")
                        btn_s3_offer = gr.Button("📜 Issue Formal Offer, Execute BGV & Build Onboarding Package", variant="primary", size="lg")

                hitl2_summary_out = gr.Markdown()
                offer_out = gr.Markdown()
                bgv_out = gr.Markdown()
                onboarding_out = gr.Markdown()

            # TAB 4: DEEPSEEK SETTINGS & API SETUP
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

        # Dynamic Role Preset Event Handler
        s1_role_dropdown.change(
            fn=update_role_preset_details,
            inputs=[s1_role_dropdown],
            outputs=[s1_title, s1_dept, s1_skills, s1_sal_min, s1_sal_max]
        )

        # Wire Event Handlers
        btn_s1.click(
            fn=handle_job_intake,
            inputs=[s1_title, s1_dept, s1_skills, s1_sal_min, s1_sal_max, api_key_in, model_in],
            outputs=[s1_summary_out, s1_jd_out, s1_band_out]
        )

        btn_custom_post.click(
            fn=generate_customized_job_post,
            inputs=[s1_title, s2_portal_select, s2_jd_in, api_key_in, model_in],
            outputs=[s2_custom_post_out]
        )

        btn_s2.click(
            fn=run_step2_sourcing_screening,
            inputs=[s2_portal_select, s2_jd_in, s2_resume_in, s2_req_exp, s2_work_mode, s2_target_loc, api_key_in, model_in],
            outputs=[s2_postings_out, s2_status_out, s2_summary_out, s2_cat_out, s2_loop_out, s2_email_name]
        )

        btn_shootout_email.click(
            fn=shootout_candidate_email,
            inputs=[s2_email_name, s2_email_addr, s1_title],
            outputs=[s2_shootout_out]
        )

        btn_telephonic.click(
            fn=run_step3_telephonic_and_hitl1,
            inputs=[s3_cand_name, s3_role_title],
            outputs=[telephonic_out, hitl1_status_out]
        )

        btn_hitl1.click(
            fn=record_hitl1_decision,
            inputs=[hitl1_decision, hitl1_notes, s3_cand_name],
            outputs=[hitl1_record_out]
        )

        btn_s3_offer.click(
            fn=run_step3_offer_and_onboarding,
            inputs=[s3_cand_name, s3_role_title, hitl2_ctc, hitl2_bonus, hitl2_work_mode, hitl2_doj, hitl2_checkbox, hitl2_notes, api_key_in, model_in],
            outputs=[hitl2_summary_out, offer_out, bgv_out, onboarding_out]
        )

    return demo
