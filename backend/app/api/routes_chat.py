"""Chat endpoints — the single entry point a farmer talks to.

The heavy lifting lives in the agent orchestrator; this layer just adapts
HTTP <-> agent and persists the turn to memory.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas import ChatRequest, ChatResponse
from app.agent.orchestrator import Orchestrator
from app.memory import store

router = APIRouter(prefix="/api", tags=["chat"])

_orchestrator = Orchestrator()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Handle one farmer message and return the agent's reply + trace.

    TODO:
      - load session (or create) via memory.store
      - call orchestrator.run(session, message)
      - persist updated farm profile, messages, and any plan/financials
    """
    session = store.get_or_create_session(req.session_id)
    result = await _orchestrator.run(session=session, message=req.message)
    store.save_turn(session, req.message, result)
    return result


@router.get("/session/{session_id}", response_model=ChatResponse)
async def get_session(session_id: str) -> ChatResponse:
    """Rehydrate a prior session (persistent memory / cross-session)."""
    return store.load_session_snapshot(session_id)
