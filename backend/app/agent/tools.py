"""Tool registry: the bridge between the LLM's tool calls and Python functions.

Each tool exposes:
  - a JSON schema (name, description, input_schema) sent to the LLM, and
  - an async `handler(**kwargs)` the orchestrator invokes when the LLM calls it.

Keeping the schema and handler together makes it trivial to add a tool: define
it here and it is automatically available to the agent + rendered in the trace.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from app.tools import crops, finance, season_plan, weather
from app.rag import retriever


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., Awaitable[Any]]

    def to_schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


# --- Tool definitions -------------------------------------------------------
# NOTE: handlers are the real implementations in app/tools/* (currently stubs).

TOOLS: dict[str, Tool] = {
    "get_weather": Tool(
        name="get_weather",
        description=(
            "Fetch REAL current + forecast weather (rainfall, temperature) for "
            "a location using the Open-Meteo API. Use before crop/fertilizer "
            "advice."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
                "days": {"type": "integer", "default": 7},
            },
            "required": ["location"],
        },
        handler=weather.get_weather,
    ),
    "recommend_crops": Tool(
        name="recommend_crops",
        description=(
            "Rank at least 3 candidate crops for the farm profile, season, and "
            "weather. Each option returns suitability, water need, risk, and a "
            "rough profit estimate. Grounded in the knowledge base."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "soil_type": {"type": "string"},
                "season": {"type": "string"},
                "water_availability": {"type": "string"},
                "weather_summary": {"type": "object"},
                "budget_bdt": {"type": "number"},
            },
            "required": ["soil_type", "season"],
        },
        handler=crops.recommend_crops,
    ),
    "build_season_plan": Tool(
        name="build_season_plan",
        description=(
            "Produce a dated calendar for the chosen crop from land preparation "
            "to harvest: sowing window, fertilizer timing, irrigation, weed/pest "
            "checkpoints, harvest."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "crop": {"type": "string"},
                "sowing_date": {"type": "string", "description": "ISO date"},
                "soil_type": {"type": "string"},
            },
            "required": ["crop"],
        },
        handler=season_plan.build_season_plan,
    ),
    "compute_financials": Tool(
        name="compute_financials",
        description=(
            "Itemized cost breakdown + expected yield, revenue, net profit, ROI, "
            "and break-even. Inspectable and internally consistent."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "crop": {"type": "string"},
                "farm_size_acres": {"type": "number"},
                "inputs": {"type": "object"},
                "expected_price_bdt_per_unit": {"type": "number"},
            },
            "required": ["crop", "farm_size_acres"],
        },
        handler=finance.compute_financials,
    ),
    "search_knowledge_base": Tool(
        name="search_knowledge_base",
        description=(
            "Retrieve grounded agronomic facts (crop calendars, fertilizer "
            "guides, soil/yield references) from the RAG knowledge base."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "k": {"type": "integer", "default": 4},
            },
            "required": ["query"],
        },
        handler=retriever.search,
    ),
}


def tool_schemas() -> list[dict[str, Any]]:
    """List of tool schemas to advertise to the LLM."""
    return [t.to_schema() for t in TOOLS.values()]


async def dispatch(name: str, params: dict[str, Any]) -> Any:
    """Invoke a tool by name with validated params."""
    if name not in TOOLS:
        raise KeyError(f"Unknown tool: {name}")
    return await TOOLS[name].handler(**params)
