# LangGraph Candidate Screening

A simple candidate-screening workflow built with LangGraph and Gemini.

## Workflow

```text
                 START
                   |
                   v
          categorize_experience
                   |
                   v
            assess_skillset
  |----------------|--------------|
  |                |              |
  v                v              v
schedule_hr   escalate_to     reject_application
_interview     _recruiter
  |                |              |
  |________________|______________|
                   |
                   v
                  END
```

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Linux/macOS**

```bash
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Gemini API key

Copy the example environment file:

```bash
cp .env.example .env
```

On Windows:

```powershell
Copy-Item .env.example .env
```

Then update `.env`:

```env
GEMINI_API_KEY=your_actual_gemini_api_key
MODEL_NAME=google_genai:gemini-3.7-flash
```

### 4. Run

```bash
python main.py
```

Example input:

```text
I have 5 years of software engineering experience with expertise in Python, FastAPI and PostgreSQL.
```

## LangGraph routing

The workflow routes candidates as follows:

- Skill match -> HR interview
- No skill match + senior-level experience -> recruiter review
- Otherwise -> rejection
