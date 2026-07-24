"""Financial projection tool (Tier-0 #5).

Itemized cost breakdown + expected yield, revenue, net profit, ROI, break-even.
The math must be INSPECTABLE and internally consistent: change an input and the
outputs change correctly. This module is pure arithmetic (no LLM), so it is the
easiest thing to unit-test — see tests/test_finance.py.
"""
from __future__ import annotations

from typing import Any


def _roi(net_profit: float, total_cost: float) -> float | None:
    return round(net_profit / total_cost, 3) if total_cost else None


async def compute_financials(
    crop: str,
    farm_size_acres: float,
    inputs: dict[str, Any] | None = None,
    expected_price_bdt_per_unit: float | None = None,
) -> dict[str, Any]:
    """Return an itemized, internally-consistent financial projection.

    Target shape:
        {
          "crop": ...,
          "farm_size_acres": ...,
          "costs": [{"item":"Seed","qty":..,"unit_cost":..,"total":..}, ...],
          "total_cost_bdt": ...,
          "expected_yield_unit": "maund",
          "expected_yield": ...,
          "price_bdt_per_unit": ...,
          "revenue_bdt": ...,
          "net_profit_bdt": revenue - total_cost,
          "roi": net_profit / total_cost,
          "break_even_price_bdt_per_unit": total_cost / expected_yield,
          "break_even_yield": total_cost / price_per_unit,
          "assumptions": ["yield/acre from KB ...", "prices from ... (mock/real)"]
        }

    Pure function target so it is deterministic and testable. Reference cost/yield
    figures come from data/seed + the KB; prices are seeded/mock until a real feed
    is wired (state this in `assumptions`).

    TODO: assemble line items from `inputs` (fertilizer/irrigation/labour/seed),
    pull per-acre yield and reference prices, and compute the derived metrics.
    Keep every derived number a direct function of the line items above.
    """
    raise NotImplementedError("Assemble line items and compute derived metrics.")
