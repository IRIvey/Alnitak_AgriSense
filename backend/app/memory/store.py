"""Memory CRUD — the thin API the routes/orchestrator use.

Wraps the ORM so the rest of the code never touches sessions directly. This is
where persistent (cross-session) memory is read and written.
"""
from __future__ import annotations

from app.api.schemas import ChatResponse
from app.memory.models import Session


def get_or_create_session(session_id: str | None) -> Session:
    """Return an existing Session (with history) or create a fresh one.

    TODO:
      - open a DB session (get_db)
      - if session_id: fetch Session + eager-load messages; else create new
      - optionally link to a Farm by owner_ref for cross-session recall
    """
    raise NotImplementedError


def save_turn(session: Session, user_message: str, result: ChatResponse) -> None:
    """Persist the user message, assistant reply, updated profile, and plan.

    TODO:
      - append Message(role="user") and Message(role="assistant")
      - update session.profile_snapshot from result.farm
      - update session.latest_plan from result.season_plan/financials
      - commit
    """
    raise NotImplementedError


def load_session_snapshot(session_id: str) -> ChatResponse:
    """Rehydrate a prior session into a ChatResponse (for GET /session/{id}).

    TODO: build ChatResponse from stored profile snapshot + latest plan.
    """
    raise NotImplementedError
