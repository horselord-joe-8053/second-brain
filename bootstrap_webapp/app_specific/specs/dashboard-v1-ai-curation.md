# Feature slice: AI curation for top 10 (dashboard-v1 ticket)

Extends **`docs/specs/dashboard-v1.md`**.

## Goal

When **`LLM_API_KEY`** is configured, rank and select the **top 10 AI news** items from RSS **candidates** using a **fixed server-side prompt** that prioritizes **the very latest** stories first, while honoring **6 US / 1 UK / 3 CN** outlet regions.

## Constraints

- **Candidates:** server fetches RSS (same feeds as v1), AI keyword prefilter, **`published` within last 72 hours UTC** (wider pool than v1 “today only”).
- **Curation:** one LLM call per cache miss (same 15-minute cache as v1); **mock LLM in CI** — no live API in unit tests.
- **Prompt (invariant):** system message states: select exactly **10** URLs from the provided list; **newest stories first**; must be **AI-related**; regional caps **6 US, 1 UK, 3 CN**; return JSON only `{"selected_urls": ["...", ...]}`.
- **Fallback:** if key missing, LLM error, or invalid JSON/URLs → use **deterministic** v1 logic (today UTC + keyword + quota).
- Response adds **`curated_by`:** `"ai"` | `"deterministic"`.

## Acceptance criteria

1. **AC-AI1:** With mocked LLM returning valid URLs, `GET /api/news/top10` returns those items (subset of candidates) and `curated_by: "ai"`.
2. **AC-AI2:** Mocked LLM enforces recency in prompt contract (unit test asserts prompt contains “latest” / recency instruction).
3. **AC-AI3:** Without `LLM_API_KEY`, behavior matches deterministic v1 and `curated_by: "deterministic"`.
4. **AC-AI4:** Invalid LLM output falls back to deterministic without 5xx.
5. **AC-AI5:** `./scripts/verify.sh` green.

## Test seams

| Seam | Tool | Notes |
|------|------|--------|
| Curator | pytest | mock HTTP to OpenAI; prompt + JSON parse |
| Integration | pytest + TestClient | patch curator or LLM boundary |

Implement per `docs/WEBAPP-TDD.md`.
