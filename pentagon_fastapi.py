# pentagon_fastapi.py
# ─────────────────────────────────────────────────────────────
# Pentagon REST API — powered by FastAPI
# Exposes Pentagon's brain over HTTP for external integrations
#
# Run with:
#   uvicorn pentagon_fastapi:app --reload
#
# Endpoints:
#   POST /ask        → Ask Pentagon a question
#   GET  /health     → Check if Ollama + API are alive
# ─────────────────────────────────────────────────────────────

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from prompt_config import (
    SYSTEM_PROMPT,
    OLLAMA_URL,
    OLLAMA_MODEL,
    OLLAMA_PARAMS,
)

# ─────────────────────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Pentagon API",
    description="Offline AI assistant powered by LLaMA3 via Ollama",
    version="1.0.0",
)

# Allow all origins — restrict this in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# Request / Response models
# ─────────────────────────────────────────────────────────────

class PromptInput(BaseModel):
    prompt: str

class PentagonResponse(BaseModel):
    reply: str
    model: str


# ─────────────────────────────────────────────────────────────
# Helper: call Ollama safely
# ─────────────────────────────────────────────────────────────

def _call_ollama(prompt: str) -> str:
    """Send a prompt to Ollama and return the text response."""
    full_prompt = SYSTEM_PROMPT + "\n\nUser: " + prompt.strip()

    try:
        res = requests.post(
            OLLAMA_URL,
            json={
                "model":  OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False,
                **OLLAMA_PARAMS,
            },
            timeout=60,
        )
        res.raise_for_status()
        data = res.json()
        reply = data.get("response", "").strip()

        if not reply:
            raise HTTPException(status_code=502, detail="Empty response from Ollama model.")

        return reply

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Ollama is not running. Start it with: ollama serve"
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Ollama timed out. The model might still be loading."
        )
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {e}")


# ─────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Check if Ollama is reachable."""
    try:
        requests.get("http://localhost:11434", timeout=3)
        return {"status": "ok", "ollama": "running", "model": OLLAMA_MODEL}
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Ollama is not running. Start it with: ollama serve"
        )


@app.post("/ask", response_model=PentagonResponse)
def ask_pentagon(data: PromptInput):
    """
    Send a question to Pentagon and get a response.

    Body:
        { "prompt": "your question here" }

    Returns:
        { "reply": "...", "model": "llama3" }
    """
    if not data.prompt or not data.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    reply = _call_ollama(data.prompt)
    return PentagonResponse(reply=reply, model=OLLAMA_MODEL)