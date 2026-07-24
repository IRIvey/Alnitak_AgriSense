"""Crop recommendation tool (Tier-0 #3).

Ranks candidate crops for the farm profile, season, and live weather. Scoring is
deterministic Python over the seed reference data (compiled from public BRRI/
BARC/DAE guides), with KB citations attached via RAG so every option names the
data behind it. The LLM never invents scores — it calls this tool.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from app.rag import retriever
from app.tools.seed_data import (
    crop_economics,
    crop_profiles,
    market_prices,
    normalize_season,
    normalize_soil,
)


def current_season(today: date | None = None) -> str:
    """Which cropping season is running right now (by month)."""
    m = (today or date.today()).month
    if 3 <= m <= 5:
        return "kharif-1"
    if 6 <= m <= 10:
        return "kharif-2"
    return "rabi"

_WATER_RANK = {"low": 0, "low-medium": 1, "medium": 2, "high": 3}
# How much water each availability class can support (rank ceiling).
_AVAIL_CEILING = {
    "rainfed": 2,       # rain-dependent: up to "medium" in monsoon
    "limited": 2,       # a few irrigations possible
    "canal": 3,
    "tubewell": 3,
    "reliable": 3,
}


def _availability_rank(water_availability: str | None, season: str | None) -> int:
    s = (water_availability or "").lower()
    for key, ceil in _AVAIL_CEILING.items():
        if key in s:
            # rainfed outside monsoon can't even support medium-need crops
            if key == "rainfed" and season == "rabi":
                return 1
            return ceil
    return 3 if not s else 2  # unknown → assume moderate


async def recommend_crops(
    soil_type: str,
    season: str,
    water_availability: str | None = None,
    weather_summary: dict[str, Any] | None = None,
    budget_bdt: float | None = None,
    farm_size_acres: float | None = None,
) -> dict[str, Any]:
    """Return >=3 ranked crop options with suitability, water need, risk,
    rough profit, and a `because` explanation naming the inputs used."""
    soil = normalize_soil(soil_type)
    norm_season = normalize_season(season)
    avail_rank = _availability_rank(water_availability, norm_season)
    acres = farm_size_acres or 1.0

    rain = (weather_summary or {}).get("total_rain_mm")
    rain_days = (weather_summary or {}).get("rain_days")

    # A short-range forecast is only decision-relevant if the target season is
    # happening NOW. A July forecast says nothing about January Boro planting.
    now_season = current_season()
    weather_applicable = norm_season == now_season
    weather_gate_note = None
    if rain is not None and not weather_applicable:
        weather_gate_note = (
            f"live forecast NOT factored into ranking: target season "
            f"'{norm_season}' is not the current season ('{now_season}'); the "
            f"forecast horizon does not reach the sowing window"
        )

    options: list[dict[str, Any]] = []
    for name, prof in crop_profiles().items():
        econ = crop_economics().get(name, {})
        in_season = norm_season in prof["seasons"] if norm_season else True

        soil_score = prof["soil"].get(soil, 0.5)
        need_rank = _WATER_RANK.get(prof["water_need"], 2)
        water_ok = need_rank <= avail_rank
        water_score = 1.0 if water_ok else max(0.0, 1.0 - 0.4 * (need_rank - avail_rank))

        # Weather nudges (live forecast data — only when the target season is
        # the current one, so the forecast actually covers the decision)
        weather_note = ""
        weather_adj = 0.0
        if rain is not None and weather_applicable:
            if prof["water_need"] in ("medium", "high") and rain < 10 and avail_rank < 3:
                weather_adj -= 0.1
                weather_note = f"only {rain} mm rain forecast — a stress risk for a {prof['water_need']}-water crop without irrigation"
            elif "waterlog" in prof.get("water_note", "") and rain > 80:
                weather_adj -= 0.15
                weather_note = f"{rain} mm forecast rain raises waterlogging risk"
            elif rain >= 10 and prof["water_need"] in ("medium", "high"):
                weather_note = f"{rain} mm rain forecast over the period supports its {prof['water_need']} water need"

        # Budget feasibility
        cost_per_acre = sum(econ.get("costs_per_acre", {}).values())
        total_cost = cost_per_acre * acres
        budget_ok = budget_bdt is None or budget_bdt >= total_cost
        budget_score = 1.0 if budget_ok else max(0.2, budget_bdt / total_cost if total_cost else 1.0)

        suitability = round(
            max(
                0.0,
                min(
                    1.0,
                    (0 if not in_season else 0.35)
                    + 0.30 * soil_score
                    + 0.20 * water_score
                    + 0.15 * budget_score
                    + weather_adj,
                ),
            ),
            2,
        )

        # Rough profit from seed economics (mock/seeded prices — disclosed)
        price = market_prices().get(name.split(" (")[0], {}).get("current") or econ.get(
            "price_bdt_per_unit", 0
        )
        yield_pa = econ.get("yield_per_acre", 0)
        profit_pa = round(yield_pa * price - cost_per_acre)

        because_parts = [
            f"{'in' if in_season else 'OUT of'} season for {norm_season or season}",
            f"{soil} soil suitability {soil_score:.1f}/1.0 ({prof['source']})",
            f"water need '{prof['water_need']}' vs availability '{water_availability or 'unknown'}'",
        ]
        if weather_note:
            because_parts.append(weather_note)
        if budget_bdt is not None:
            because_parts.append(
                f"needs ~{total_cost:,.0f} BDT for {acres:g} acre(s) vs budget {budget_bdt:,.0f}"
                + ("" if budget_ok else " — OVER budget")
            )

        options.append(
            {
                "crop": name,
                "suitability": suitability,
                "in_season": in_season,
                "water_need": prof["water_need"],
                "risk": prof["risk"],
                "risk_note": prof["risk_note"],
                "sowing_window": prof["sowing_window"]["label"],
                "rough_cost_bdt_per_acre": cost_per_acre,
                "rough_profit_bdt_per_acre": profit_pa,
                "rough_profit_bdt_total": round(profit_pa * acres),
                "because": "; ".join(because_parts),
            }
        )

    options.sort(key=lambda o: (o["in_season"], o["suitability"]), reverse=True)
    top = options[:5]

    # Attach KB citations for the top pick's season decision (grounding)
    kb_refs = await retriever.search_compact(
        f"which crop to plant {norm_season or season} season {soil} soil Bangladesh", k=2
    )

    result: dict[str, Any] = {
        "inputs_used": {
            "soil_type": soil,
            "season": norm_season or season,
            "current_season": now_season,
            "weather_applied_to_ranking": weather_applicable,
            "water_availability": water_availability,
            "budget_bdt": budget_bdt,
            "farm_size_acres": acres,
            "weather_summary": weather_summary,
        },
        "options": top,
        "kb_references": kb_refs,
        "note": "profit estimates use seeded reference prices (see data/seed) — disclosed as mock",
    }
    if weather_gate_note:
        result["weather_note"] = weather_gate_note
    return result
