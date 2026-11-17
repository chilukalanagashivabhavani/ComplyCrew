# ComplyCrew – AI-Powered Privacy Compliance Assistant

ComplyCrew is a prototype for reviewing privacy policies and related documents against a local privacy compliance rulebook. It combines a locally served Gemma 2B model through Ollama, sentence-transformer embeddings, ChromaDB retrieval, and a staged set of Python agents to surface findings for human review.

> **Important:** ComplyCrew is an analysis aid, not legal advice or a certification tool. The included rulebook is a prototype and should be reviewed by qualified privacy professionals before it is relied on.

## Problem

Privacy requirements are expressed across long policies and operational documents. Reviewing them manually against a checklist takes time, and it can be difficult to tie a concern to the specific document wording and requirement. ComplyCrew demonstrates a structured workflow that helps surface possible gaps for a person to assess.

## Objectives

- Break documents into clauses for individual review.
- Retrieve relevant requirements from the project rulebook.
- Use specialized agents to assess and verify potential findings.
- Present findings, risk levels, and human-review indicators through a UI or API.
- Run language-model inference locally through Ollama.

## Features implemented

- Upload and analyze TXT, PDF, and DOCX documents.
- Extract document text and split it into clauses.
- Retrieve related rules using `all-MiniLM-L6-v2` embeddings and ChromaDB.
- Call Gemma 2B through Ollama for clause extraction, matching, risk scoring, and verification.
- Provide a Streamlit interface and a separate React/Vite interface backed by FastAPI.
- Expose FastAPI root, health, and `/analyze` upload routes.
- Mark findings for human review and show analysis results in the UI.

The React app's document history is held in frontend component state; it is not persistent storage. ChromaDB is a local vector store for rules, not an application account or document database.

## Technology stack

| Area | Technologies found in the source |
| --- | --- |
| Language/runtime | Python, JavaScript, React |
| Frontend | React 19, Vite 8, Axios, Lucide React |
| Alternate UI | Streamlit |
| API | FastAPI, Uvicorn, `python-multipart` |
| AI inference | Ollama HTTP API, `gemma2:2b` |
| Retrieval | Sentence Transformers (`all-MiniLM-L6-v2`), ChromaDB |
| Document parsing | pypdf, python-docx |

## System architecture

```text
                       ┌────────────────────────────┐
                       │ React/Vite UI (port 5173)  │
                       └─────────────┬──────────────┘
                                     │ POST /analyze
                                     ▼
                       ┌────────────────────────────┐
                       │ FastAPI: api.py (port 8000)│
                       └─────────────┬──────────────┘
                                     │
             ┌───────────────────────┼──────────────────────┐
             ▼                       ▼                      ▼
       Document parsing       Agent sequence       ChromaDB + rulebook
                                     │
                                     ▼
                              Ollama / Gemma 2B

       Alternate UI: app.py (Streamlit, direct agent calls)
```

`backend/main.py` is another FastAPI application with overlapping routes. The React frontend is configured for `api.py` at `127.0.0.1:8000`; use it for the documented React workflow. The two API modules have different response formats and CORS settings.

## Project structure

```text
.
├── agents/
│   ├── extractor_agent.py       # Clause extraction via Gemma/Ollama
│   ├── rule_matcher_agent.py    # Rule retrieval and model-assisted matching
│   ├── risk_scorer_agent.py     # Potential risk assessment
│   ├── verifier_agent.py        # Checks a candidate finding
│   └── report_writer_agent.py   # Writes a report from prior agent results
├── backend/main.py              # Alternate FastAPI app
├── data/rulebook.txt            # Prototype compliance rules (source asset)
├── frontend/                    # React/Vite web interface
├── sample/sample_privacy_policy.txt
├── api.py                       # FastAPI app used by the React UI
├── app.py                       # Streamlit UI
├── pipeline.py                  # Script-style analysis pipeline
├── vector_store.py              # ChromaDB rulebook initialization/retrieval demo
└── requirements.txt             # Python dependencies
```

Generated ChromaDB state is stored under `data/chroma_db/` at runtime and is excluded from Git. The rulebook and sample document are source assets and remain included.

## Agents and compliance workflow

In the API path, `api.py` calls extraction, rule matching, risk scoring, and verification, then formats findings for its response. The Streamlit flow also calls the report writer to produce a narrative report. `pipeline.py` contains a separate script-style flow, so agent usage depends on the chosen entry point.

1. **Extractor Agent** (`agents/extractor_agent.py`) sends document text to Gemma via Ollama and returns extracted clauses.
2. **Rule Matcher Agent** (`agents/rule_matcher_agent.py`) embeds a clause, retrieves likely rulebook matches from ChromaDB, and uses Ollama to assess relevance.
3. **Risk Scorer Agent** (`agents/risk_scorer_agent.py`) assesses a potential issue against its clause and matched rule.
4. **Verifier Agent** (`agents/verifier_agent.py`) checks a candidate finding and provides verification/confidence details.
5. **Report Writer Agent** (`agents/report_writer_agent.py`) creates a report from upstream results in flows that call it.

The outputs are model-generated suggestions. A human should validate the cited clause, applicable rule, risk, and remediation before acting on a finding.

## Prerequisites

- Python 3.10 or newer (the existing local environment was Python 3.12).
- Node.js and npm for the React interface.
- Ollama installed and running locally, with `gemma2:2b` available.
- Internet access on first run may be needed to download packages, the embedding model, and the Ollama model.

## Installation

Run commands from the repository root.

### 1. Create a Python environment

**Windows PowerShell:**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Install the local model

```bash
ollama pull gemma2:2b
```

Start Ollama using its normal platform-specific service/app command and leave it running. The agents call `http://localhost:11434/api/chat` directly. No API key or `.env` setting is used by the current source.

### 3. Install frontend packages (React UI only)

```bash
cd frontend
npm ci
cd ..
```

The first backend run initializes/updates the local vector store using `data/rulebook.txt` and may download `all-MiniLM-L6-v2` from the model hub.

## Run the application

Choose one UI path.

### React + FastAPI

Terminal 1, from the repository root:

```bash
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
cd frontend
npm run dev
```

Open the Vite URL shown in the terminal (normally `http://localhost:5173`). The frontend posts uploads to `http://127.0.0.1:8000/analyze`.

### Streamlit

From the repository root, with Ollama running:

```bash
python -m streamlit run app.py
```

Streamlit processes uploads through its direct agent workflow. Supported upload extensions are PDF, DOCX, and TXT.

### API health check

With FastAPI running, open `http://127.0.0.1:8000/health`. Interactive API documentation is at `http://127.0.0.1:8000/docs`.

## Sample usage

1. Start Ollama and ensure `gemma2:2b` is installed.
2. Start either the React/FastAPI pair or Streamlit.
3. Upload `sample/sample_privacy_policy.txt` or another TXT, PDF, or DOCX document.
4. Start analysis and inspect each finding, its matched requirement, risk, and review status.
5. Verify outputs against the source document and applicable authoritative requirements.

## Screenshots

No screenshots are included yet. Add genuine UI screenshots when available, such as:

- `docs/screenshots/dashboard.png` — upload and overview.
- `docs/screenshots/findings.png` — findings using non-sensitive sample content.

## Security and privacy

- The current agents send document text to local Ollama at `localhost:11434`; no hosted LLM API is configured in the source reviewed.
- Uploaded content is processed by the running application. Avoid uploading confidential documents unless your local environment and data-handling practices are appropriate.
- Generated ChromaDB data, environments, and `.env` files are ignored by Git.
- Do not commit credentials or real customer documents. `.env.example` is unnecessary until the app reads environment settings.
- This prototype does not replace legal review or guarantee compliance.

## Future enhancements

- Centralize settings such as API URL, model name, and CORS origins in validated environment configuration.
- Add automated tests for parsing, agents, API response formats, and error handling.
- Unify the duplicated FastAPI implementations and their response schemas.
- Add persistent analysis history with retention and deletion controls.
- Add configurable, versioned jurisdiction-specific rulebooks with source citations.
- Improve upload limits, validation, and deployment security before accepting untrusted or sensitive documents.
- Add deployment guidance and genuine, privacy-safe screenshots.

## Author and contact

Author/contact details were not present in the repository. Add your preferred name, GitHub profile, and professional contact before publishing.
