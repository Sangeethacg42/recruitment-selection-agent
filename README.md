# 🤖 AI Agent for Automating Recruitment & Selection

An autonomous HR Talent Acquisition & Selection AI Agent built with **Python**, **`uv`**, **LangGraph** (featuring iterative quality reflection/evaluation loops), **Gradio** web interface, and the **DeepSeek API**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-orange)
![Gradio](https://img.shields.io/badge/Frontend-Gradio-red)
![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek--API-purple)

---

## 🌟 Key Features

1. **Iterative Evaluation & Reflection Loop (LangGraph)**:
   - **Screener Node**: Evaluates candidate resumes against Job Description across Technical Skills, Relevant Experience, Education, and Cultural Fit.
   - **QA Audit Evaluator Node**: Inspects the screener's output for missing dealbreakers, unverified claims, or hallucinations.
   - **Conditional Feedback Loop**: If QA quality score < 80 or needs revision, automatically loops back to `screener_node` for refinement (up to max reflection limit).
   - **Interview Kit Node**: Generates role-specific behavioral & technical questions with ideal answer rubrics once screening is validated.

2. **DeepSeek API Integration & Robust Fallback**:
   - Uses OpenAI-compatible client (`https://api.deepseek.com`) supporting `deepseek-chat` and `deepseek-reasoner` models.
   - Includes a built-in Mock engine so you can test and demonstrate the full application instantly out-of-the-box even without an active API key!

3. **Multi-Tab Gradio Web UI**:
   - **Single Candidate Screening & Loop Inspector**: Full candidate evaluation with step-by-step reflection loop inspection.
   - **Multi-Candidate Leaderboard**: Rank multiple candidates side-by-side against a single JD.
   - **AI Interview Kit Generator**: Custom questions, rationale, and sample answer rubrics.
   - **Settings Tab**: Dynamic API Key configuration, model selection, and live connection test button.

---

## 🏗️ Architecture & Graph Loop Workflow

```
               +----------------------------------+
               |  Parse JD & Candidate Resume    |
               +----------------------------------+
                                |
                                v
                    +-----------------------+
                    |    screener_node      | <------+
                    +-----------------------+        |
                                |                    |
                                v                    | Refinement
                    +-----------------------+        | Loop
                    |    evaluator_node     |        | (Score < 80)
                    +-----------------------+        |
                                |                    |
                     [ should_continue? ] -----------+
                                |
                   (Score >= 80 or Max Loops)
                                |
                                v
                    +-----------------------+
                    |  interview_gen_node   |
                    +-----------------------+
                                |
                                v
                          ((   END   ))
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites & Installation via `uv`

Ensure you have [`uv`](https://github.com/astral-sh/uv) installed.

```bash
# Clone or enter project directory
cd c:/Users/Lenovo/Desktop/Sangeetha--Agent--1

# Install dependencies using uv
uv sync
```

### 2. Configure DeepSeek API Key (Optional)

Create a `.env` file or set the environment variable:

```bash
cp .env.example .env
```

Edit `.env`:
```env
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```
*(Note: You can also enter or update your API key anytime directly inside the Gradio UI Settings tab!)*

### 3. Launch the Application

Run the application using `uv`:

```bash
uv run main.py
```

Open your browser at: `http://127.0.0.1:7860`

---

## 📂 Project Structure

```
.
├── pyproject.toml               # Project metadata & uv dependencies
├── .env.example                 # Environment variable template
├── main.py                      # App entrypoint launching Gradio server
├── README.md                    # Project documentation
└── src/
    └── recruitment_agent/
        ├── __init__.py
        ├── config.py            # Global configuration settings
        ├── llm.py               # DeepSeek LLM wrapper & mock generator
        ├── models.py            # Pydantic schemas & AgentState TypedDict
        ├── graph.py             # LangGraph state machine & reflection loop
        ├── utils.py             # Built-in sample JDs and Resumes
        └── ui.py                # Gradio UI components & layouts
```

---

## 🧪 Testing & Verification

To run a quick verification of the agent state graph in Python:

```bash
uv run python -c "from recruitment_agent.graph import build_recruitment_graph; graph = build_recruitment_graph(); print('Graph compiled successfully!')"
```
