"""Season plan tool (Tier-0 #4).

For the chosen crop, produce a DATED calendar from land preparation to harvest:
sowing window, fertilizer timing, irrigation, weed/pest checkpoints, harvest.

Ground stage timings and intervals in the crop calendar retrieved from the KB.
"""
from __future__ import annotations

from typing import Any


async def build_season_plan(
    crop: str,
    sowing_date: str | None = None,
    soil_type: str | None = None,
) -> dict[str, Any]:
    """Return a dated season calendar.

    Shape:
        {
          "crop": "Boro Rice",
          "sowing_window": {"start": "ISO", "end": "ISO"},
          "stages": [
             {"stage":"Land preparation","date":"ISO","action":"...","because":"..."},
             {"stage":"Sowing","date":"ISO", ...},
             {"stage":"Fertilizer - basal", ...},
             {"stage":"Irrigation", ...},
             {"stage":"Weed check", ...},
             {"stage":"Pest checkpoint", ...},
             {"stage":"Harvest","date":"ISO", ...}
          ]
        }

    TODO:
      - retriever.search(f"{crop} crop calendar growth stages days after sowing")
      - anchor to sowing_date (default: next suitable window from weather) and
        offset each stage by its days-after-sowing from the KB
    """
    raise NotImplementedError("Build dated calendar from KB crop-calendar offsets.")
