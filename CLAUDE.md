# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WhatsApp chatbot for medical clinics built with FastAPI + LangGraph. Handles FAQ (RAG-augmented), appointment scheduling (multi-turn stateful), exam result queries, and human escalation. Receives messages via Meta Cloud API webhook and replies through the same API.

## Commands

**Install dependencies:**
```bash
pip install -e .
# or faster:
uv pip install -e .
```

**Run dev server:**
```bash
uvicorn app.main:app --reload
```

**Run full stack (app + PostgreSQL):**
```bash
docker compose up
```

**Test:**
```bash
pytest           # all tests
pytest -v -s     # verbose with prints
pytest tests/test_webhook.py::test_name  # single test
```

**Lint & format:**
```bash
ruff check app tests
ruff format app tests
```

## Architecture

### Request Flow

```
WhatsApp user → Meta Cloud API → POST /webhook/message
  → app/api/webhook.py (validates HMAC, extracts phone + text)
  → app/agent/graph.py (LangGraph, thread_id = phone number)
    → classify node (intent: faq | agendamento | resultado | humano | outro)
    → routed node (faq uses RAG, agendamento is multi-turn)
  → app/services/whatsapp.py (POST back to Meta Graph API)
```

The webhook **always returns HTTP 200** — errors are logged to stderr and swallowed so Meta never retries.

### LangGraph Agent (`app/agent/`)

- **`state.py`**: `AgentState` holds `messages` (LangChain messages), `phone`, and `intent`
- **`graph.py`**: Builds the compiled graph; lifecycle manages PostgreSQL checkpointer and RAG vectorstore
- **Nodes** (`nodes/`): Each is a pure async function `(state) → dict`. Nodes write new fields into state; they don't mutate in place
- **Thread persistence**: `thread_id = phone_number` → conversation history survives across webhook calls via `AsyncPostgresSaver` (PostgreSQL in prod, SQLite locally)

### RAG System (`app/rag/`)

- Loads `.pdf` and `.txt` files from `docs/` at startup
- Splits into 500-char chunks (50 overlap), embeds with OpenAI, stores in Chroma
- `faq.py` retrieves top-4 chunks and injects them into the system prompt
- RAG is silently skipped if `docs/` is empty

### Configuration (`app/config.py`)

All settings via `pydantic-settings` (reads from `.env`):

| Variable | Notes |
|---|---|
| `OPENAI_API_KEY` | Required |
| `MODEL_NAME` | Default: `gpt-4o-mini` |
| `DATABASE_URL` | SQLite locally, PostgreSQL URL on Render |
| `META_ACCESS_TOKEN` | WhatsApp Cloud API token |
| `META_PHONE_NUMBER_ID` | Sender phone number ID |
| `META_WEBHOOK_VERIFY_TOKEN` | Token for GET subscription challenge |
| `META_APP_SECRET` | Optional HMAC signature validation |

Copy `.env.example` to `.env` to get started.

## Key Conventions

- All node handlers and service calls are `async def`
- Graph nodes return a `dict` with only the state keys they modify
- The `classify` node uses OpenAI structured output (no free-form text) for deterministic routing
- Adding a new intent requires: new node in `nodes/`, new edge in `graph.py`, and updating the classifier's intent enum
- Place clinic knowledge documents in `docs/` as `.txt` or `.pdf`; they are loaded into RAG automatically on startup
