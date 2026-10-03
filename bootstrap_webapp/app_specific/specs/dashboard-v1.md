# Feature: Personal Dashboard v1 — AI news top 10

## Goal

One-page personal dashboard that shows **10 AI-related news items published today** (UTC), drawn from RSS feeds with a fixed regional mix: **6 United States**, **1 United Kingdom**, **3 China (PRC)** media outlets.

## Constraints

- **Stack:** existing React + FastAPI factory; `./scripts/verify.sh` is the merge gate.
- **Data:** server-side RSS fetch only; frontend calls **`GET /api/news/top10`** (and **`GET /health`**) — no browser RSS, no third-party news API keys in v1.
- **Feed list:** defined in backend config (`app/news/feeds.py` or YAML loaded at startup) with exactly **6** `region=us`, **1** `region=uk`, **3** `region=cn` entries; each entry has `id`, `outlet_name`, `feed_url`, `region`.
- **AI relevance:** item included only if **title** or **summary/description** matches case-insensitive AI keyword list (minimum: `ai`, `artificial intelligence`, `machine learning`, `llm`, `large language model`, `generative ai`, `deep learning`, `openai`, `anthropic`, `chatgpt`) — configurable in one module.
- **Today filter:** keep items whose `published` parses to **today’s UTC date**; if fewer than 10 after filter, return fewer and set response field `partial: true` (do not backfill with older days in v1).
- **Quota assembly:** among today’s AI items, select up to regional caps (6/1/3), newest first within each region, until **10** total or exhausted.
- **Cache:** in-memory cache of aggregated result TTL **15 minutes**; `Refresh` on UI triggers fetch with `?refresh=true` bypassing cache.
- **Dev ports:** API **8900**, UI **5973**; CORS aligned (`APP_BACKEND_PORT`, `APP_FRONTEND_PORT`, `VITE_API_BASE_URL`).
- **Logging:** do not log full article bodies; outlet fetch errors may log outlet `id` and status only.
- **Non-goals:** auth, accounts, saved articles, non-AI sections, push notifications, mobile native apps, paid Reuters/authenticated feeds.

## Acceptance criteria

### API

1. **AC-A1:** `GET /health` returns `{ "status": "ok" }`.
2. **AC-A2:** `GET /api/news/top10` returns JSON `{ "items": [...], "partial": boolean, "fetched_at": "<iso8601>" }` where each item has `title`, `url`, `outlet_name`, `region` (`us`|`uk`|`cn`), `published` (ISO8601).
3. **AC-A3:** With mocked RSS fixtures in tests, response respects regional caps and **≤ 10** items.
4. **AC-A4:** `?refresh=true` bypasses cache (tested via cache mock or timestamp change).
5. **AC-A5:** When all feeds fail in tests, returns **502** with clear `detail` (or `200` with `items: []` and `partial: true` — pick one and test; **default: 200 empty list + partial true** for resilient UI).

### UI

6. **AC-U1:** Page title / heading identifies **Personal Dashboard** and AI top-10 purpose.
7. **AC-U2:** On load, fetches top-10 and renders a **neat ordered list** (10 or fewer) with region badge and external link per row.
8. **AC-U3:** **Refresh** control re-fetches with refresh query; shows loading state while pending.
9. **AC-U4:** Fetch failure shows accessible error message (`role="alert"`).
10. **AC-U5:** `./scripts/verify.sh` passes; CI runs same script when present.

## UI & layout

- Single route `/` — dashboard only.
- Header: app name + subtitle (“Top 10 AI news today”).
- Main: vertical list or compact cards; region badge left or top; outlet as secondary text.
- Footer or header: last updated from `fetched_at`.
- **UI-CHOOSE** before final polish (`dashboard-v1`); until then functional layout OK.

## Accessibility (a11y)

- Refresh: `<button>` with accessible name **Refresh news**.
- Headlines: links with visible text; `rel="noopener noreferrer"` on external URLs.
- Loading: `role="status"` or `aria-busy` on list container while loading.
- Errors: `role="alert"`.

## Out of scope

- User configuration of outlets in UI
- Translation of Chinese headlines
- Historical date picker
- LLM summarization (keyword filter only)

## Test seams (proposed)

| Area | Seam | Notes |
|------|------|--------|
| API | pytest + `TestClient` | health; top10 with injected RSS XML fixtures |
| RSS fetch | Mock HTTP / injectable fetcher | no live network in CI |
| AI + date filter | pytest unit tests | keyword + UTC today boundary |
| Quota | pytest unit tests | 6/1/3 caps |
| UI | Vitest + RTL | heading, list from mock fetch, refresh, error alert |

Implement tests at these seams per `docs/WEBAPP-TDD.md` — agent applies **as written**; no human confirmation required.
