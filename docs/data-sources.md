# Data sources (real vs mock disclosure)

Keep this file honest — it backs the real-vs-mock table in the root README, which
the hackathon submission explicitly requires.

## Real / live
- **Weather** — [Open-Meteo](https://open-meteo.com/) forecast + geocoding APIs.
  Keyless. Returns real rainfall, temperature, precipitation probability.

## Real / collected (RAG knowledge base)
Add each source you ingest into `backend/data/knowledge_base/`, with a link:

| Document | Topic | Source URL | Ingested? |
|----------|-------|------------|-----------|
| _e.g._ BRRI Boro rice calendar | crop calendar | _add link_ | ⬜ |
| _e.g._ BARC Fertilizer Recommendation Guide | fertilizer doses | _add link_ | ⬜ |
| _e.g._ DAE crop production guides | sowing/harvest | _add link_ | ⬜ |
| _e.g._ Soil suitability references | soil × crop | _add link_ | ⬜ |

> Suggested public sources (Bangladesh): BRRI, BARI, BARC, DAE (Department of
> Agricultural Extension), and FAO crop guides. Verify licenses allow reuse.

## Mock / seeded (disclosed)
- **Market prices** — `backend/data/seed/market_prices.json` (placeholder BDT
  values). Replace with a real price board feed if one is wired.
- **Supplier catalog** — `backend/data/seed/suppliers.json` (mock; a seeded
  catalog is explicitly permitted by the brief).

## Sandbox / simulated
- **bdapps CaaS charging** — `backend/app/bdapps/caas.py` simulates the
  charge → deduction → receipt flow. Set `BDAPPS_SANDBOX=false` with real
  credentials to hit the actual bdapps sandbox endpoint.
