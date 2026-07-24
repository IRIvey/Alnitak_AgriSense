"""Crop recommendation tool (Tier-0 #3).

Ranks >=3 candidate crops for the farm profile, season, and weather. Each option
must carry: suitability, water need, risk level, and a rough profit estimate.

Grounding: pull crop suitability + water/yield facts from the RAG knowledge base
(app/rag/retriever.py) rather than model recall. The scoring here should combine
retrieved agronomic facts with the live weather summary.
"""
from __future__ import annotations

from typing import Any


async def recommend_crops(
    soil_type: str,
    season: str,
    water_availability: str | None = None,
    weather_summary: dict[str, Any] | None = None,
    budget_bdt: float | None = None,
) -> list[dict[str, Any]]:
    """Return a ranked list of >=3 crop options.

    Each option shape:
        {
          "crop": "Boro Rice",
          "suitability": 0.0-1.0,
          "water_need": "high|medium|low",
          "risk": "low|medium|high",
          "rough_profit_bdt_per_acre": int,
          "because": "names the soil/season/weather/KB facts behind the score"
        }

    TODO:
      - retriever.search(f"{season} crops for {soil_type} soil ...")
      - score candidates on soil match, season fit, water availability vs need,
        and weather (e.g. penalise high-water crops in a low-rain forecast)
      - attach an explainable `because` string per option
    """
    raise NotImplementedError("Score candidates from KB + weather; return >=3 ranked.")
