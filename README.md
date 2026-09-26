# Vera — AI Merchant Growth Message Engine

Production-oriented submission for the magicpin **Vera — Build the Message Engine** challenge.

## Overview

Vera is a **stateful decision engine**, not a generic chatbot. Python/rules decide **what** to say and **when**; an optional LLM only polishes **how** (with deterministic category fallbacks).

```
Context → Opportunity Engine → Suppression Engine → Message Planner → LLM/Fallback → Validator → API
```

## Architecture

| Layer | Role |
|--------|------|
| **Opportunity Engine** | Ranks signals; picks one dominant opportunity |
| **Suppression Engine** | Dedupes ticks; re-opens on material context change |
| **Intent Engine** | YES / NO / LATER / QUESTION / OBJECTION / NEW_INTENT / AUTO_REPLY / HOSTILE |
| **State machine** | Conversation transitions for `/v1/reply` |
| **Category handlers** | Dentists, salons, restaurants, gyms, pharmacies copy |
| **LLM client** | Optional; `temperature=0`; falls back if missing or invalid |

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/healthz` | Liveness + context counts |
| GET | `/v1/metadata` | Team / approach metadata |
| POST | `/v1/context` | Idempotent context push (versioned) |
| POST | `/v1/tick` | Proactive actions (max 20/tick) |
| POST | `/v1/reply` | Merchant/customer reply handling |

## Local setup

```bash
cd "magicpin-ai-challenge 2"
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
set PORT=8080
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Environment variables

See `.env.example`: `PORT`, `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`, `BOT_URL`.

Without `LLM_API_KEY`, the engine uses **deterministic category templates** only.

## Tests

```bash
python -m pytest tests/ -q
```

## Judge simulator

1. Start the bot on `http://localhost:8080` (matches default `BOT_URL` in `judge_simulator.py`).
2. Run:

```bash
python judge_simulator.py
```

Set `LLM_PROVIDER=heuristic` in `judge_simulator.py` (or leave `LLM_API_KEY` empty) for offline scoring.

Scenarios: `warmup`, `phase2_short`, `auto_reply_hell`, `intent_transition`, `hostile`, `all`, `full_evaluation`.

## Docker

```bash
docker build -t vera-message-engine .
docker run -p 8080:8080 -e PORT=8080 vera-message-engine
```

## Deploy (Render)

1. New **Web Service** → connect repo or upload.
2. **Build**: `pip install -r requirements.txt`
3. **Start**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set health check path: `/v1/healthz`
5. Set public URL as `BOT_URL` for the judge.

## Design notes

- **Recent searches**: normalized (case, punctuation, hyphens); ranked with offer-match boost.
- **Suppression**: trigger `suppression_key` + fingerprint (count/version/delta); same tick → no duplicate pitch.
- **Determinism**: no randomness; LLM optional; fallback templates are stable.
- **Anti-hallucination**: validator blocks URLs/taboo; templates use payload/digest/merchant fields only.

## Project layout

```
app/
  api/          # FastAPI routes
  engine/       # Opportunity, suppression, intent, planner, composer
  categories/   # Vertical-specific fallback copy
  llm/          # Optional LLM + fallback
  storage/      # In-memory context + state (Redis-ready interfaces)
  models/       # Pydantic models
tests/
bot.py          # Canonical compose() + respond() for harness
```
