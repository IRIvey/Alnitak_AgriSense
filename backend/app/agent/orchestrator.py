"""The agent orchestrator — the tool-calling loop that makes this an *agent*.

Loop shape (per farmer turn):
    1. Build system prompt (inject missing-field hints from memory).
    2. Ask the LLM with the conversation + tool schemas.
    3. If the LLM requests tool call(s): run them, record to trace, feed the
       results back, and repeat.
    4. When the LLM returns prose with no tool call, that's the reply.

This is deliberately a hand-written loop (not a black-box framework) so the
trace captures every param sent and value returned — which is exactly what the
judges want to inspect.
"""
from __future__ import annotations

from app.agent import trace as trace_mod
from app.agent.llm import LLMClient
from app.agent.prompts import build_system_prompt
from app.agent.tools import dispatch, tool_schemas
from app.api.schemas import ChatResponse, FarmProfile
from app.memory.models import Session

MAX_STEPS = 8  # safety bound on tool-call iterations per turn


class Orchestrator:
    def __init__(self) -> None:
        self.llm = LLMClient()

    async def run(self, session: Session, message: str) -> ChatResponse:
        """Handle one farmer message end to end.

        TODO (implementation order for Tier 0):
          1. Load farm profile + message history from `session`.
          2. missing = FarmProfile(...).missing_fields()
          3. system = build_system_prompt(missing)
          4. Iterate the tool-calling loop below.
          5. Extract structured artifacts (crop_options / season_plan /
             financials) from tool results to return alongside the reply.
        """
        sid = session.id
        farm: FarmProfile = session.farm_profile or FarmProfile()

        system = build_system_prompt(farm.missing_fields())
        conversation = session.to_llm_messages() + [
            {"role": "user", "content": message}
        ]

        reply_text = ""
        for _ in range(MAX_STEPS):
            resp = await self.llm.complete(
                system=system, messages=conversation, tools=tool_schemas()
            )

            if resp.get("text"):
                trace_mod.record(sid, "message", summary=resp["text"])
                reply_text = resp["text"]

            tool_calls = resp.get("tool_calls") or []
            if not tool_calls:
                break

            for call in tool_calls:
                trace_mod.record(
                    sid, "tool_call", tool=call["name"], params=call["input"]
                )
                result = await dispatch(call["name"], call["input"])
                trace_mod.record(
                    sid, "tool_result", tool=call["name"], result=result
                )
                conversation.append(
                    {"role": "tool", "tool_call_id": call["id"], "content": result}
                )

        return ChatResponse(
            session_id=sid,
            reply=reply_text,
            farm=farm,
            trace=[],  # frontend fetches full trace via /api/trace/{sid}
        )
