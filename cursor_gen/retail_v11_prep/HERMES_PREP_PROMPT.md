<h1 id="hermes-prep-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Hermes prompt — retail PDFs → LLM Wiki</h1>

Copy everything inside the fenced block below into **Hermes Desktop** (after running `01_copy_manuals.sh`).

```text
You are on my Mac helping finish Samsung retail Second Brain prep. Repo: /Users/jjw8053/projects/second_brain.

Goals (do in order, confirm each step):

1. LLM Wiki app is running (127.0.0.1:19828). If not, tell me to start Nashsu LLM Wiki.

2. Use llm_wiki MCP (or Nashsu UI): set project to the absolute path:
   /Users/jjw8053/projects/second_brain/brain/retail
   Not the legacy brain/ root.

3. Verify raw PDFs exist (6 files as user-guide.pdf + repair-guide.pdf under):
   brain/retail/raw/sources/samsung-docs/a15/
   brain/retail/raw/sources/samsung-docs/a16/
   brain/retail/raw/sources/samsung-docs/a25/

4. Trigger source rescan / ingest for this project so PDFs compile into brain/retail/wiki/.
   Wait for ingest to finish (or tell me if queue is still running).

5. Smoke query-retail-brain wiki path only:
   - llm_wiki_search with query: "Galaxy A15 5G battery replacement" (or similar)
   - llm_wiki_read_file on one top wiki path under brain/retail/wiki/
   Report the wiki file paths you used.

6. Do NOT load PostgreSQL or run Docker — I will run cursor_gen/retail_v11_prep/03_pg_up_and_load.sh separately.

7. If query-retail-brain skill is not installed, install harness/second-brain/skills/query-retail-brain per harness docs.

Stop with a short checklist: project path set, rescan done, N wiki pages visible, one search + read succeeded.
```

**Note:** Ticket A/B (V1 vs V1.1) is **Postgres + scripts**, not Hermes — run `04_run_ab_postgres.sh` after step 03.
