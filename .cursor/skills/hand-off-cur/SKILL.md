---
name: hand-off-cur
description: >-
  Explicit /hand-off-cur only. Generate a new-chat handoff from the current session,
  discover relevant docs, write tmp/handoff/HAND_OFF_<timestamp>_<Title>.md and
  tmp/handoff/latest.md. Use when the user types /hand-off-cur.
disable-model-invocation: true
---

# hand-off-cur — session handoff for a new Agent chat

Portable workflow for **any repository**. Trigger only via **`/hand-off-cur`** (do not auto-apply).

## Outcomes

1. **On disk:** `tmp/handoff/HAND_OFF_<YYYYMMDD-HHmmss>_<TitleKey>.md` and **`tmp/handoff/latest.md`** (same content as the timestamped file).
2. **In chat:** A **copy-paste “New chat handoff” block** (same substance as the file) so the user can start `Cmd+N` and paste immediately.

Create **`tmp/handoff/`** idempotently (`mkdir -p`). Ensure **`tmp/handoff/`** is listed in **`.gitignore`** when the file exists; if missing, append one line `tmp/handoff/` (do not remove other ignore rules).

## Filename

| Part | Rule |
|------|------|
| Prefix | `HAND_OFF_` |
| Timestamp | `YYYYMMDD-HHmmss` — prefer **user_info “today” timezone** when present; else UTC |
| Title key | Chat title → **CamelCase**, **max 10 characters** (letters/digits only). Drop spaces/punctuation; capitalize word starts then join. Examples: `Retail Bm25 options` → `RetailBm25`; `New Chat` → `NewChat` |
| Fallback title key | `Session` if title missing or sanitizes to empty |
| Suffix | `.md` |

**Example:** `tmp/handoff/HAND_OFF_20261012-165600_RetailBm25.md`

**Chat title (required for TitleKey and Handoff source):**

1. Use the **Cursor chat tab title** if it appears anywhere in session/context (sidebar label, user quote, screenshot text).
2. If **not** available, **stop and ask exactly one question** before writing files: **“Tab title?”** — wait for the user’s reply; use that string for TitleKey + **Handoff source → Chat title**.
3. **Do not** infer TitleKey from thread topic, git branch, or filenames when step 2 was needed.

**TitleKey from title string:** drop punctuation; split words; CamelCase; **max 10** letters/digits (e.g. `F1 - Markdown extraction process` → `F1Markdown`).

## Chat transcript (required for important files)

Before finalizing **Reference documents** and **Files touched**, read the **last 24 hours** of the **current chat window** transcript (not only the visible context window).

| Step | Action |
|------|--------|
| Locate file | Prefer **`transcript_location`** from session/system context (`…/agent-transcripts/<uuid>/<uuid>.jsonl`). Else: under `~/.cursor/projects/<workspace-slug>/agent-transcripts/`, pick the **current** transcript (newest mtime among `**/*.jsonl` tied to this thread, or UUID matching the chat if known). |
| Time window | Keep lines whose message **`timestamp`** (in `<timestamp>…</timestamp>` on user turns) is **≥ now − 24h** (use user_info timezone when given). If a line has no timestamp, include it only when the file’s recent tail clearly belongs to this session. |
| How to read | Stream/search the JSONL (do not load multi‑MB files whole into the reply). Use **`Grep`** on path patterns and keywords; sample windows around matches. |
| Extract | Repo paths (`docs/…`, `scripts/…`, `*.md`, `*.mdc`), **`@-mentioned`** paths, **`Read`/`Write` tool targets**, plans/specs named in prose, branches/features repeated in the thread. |

Merge transcript findings with visible chat turns. **Do not** paste raw JSONL or long tool output into the handoff file.

## Session inputs

Use **this conversation** (visible turns **plus** § Chat transcript). Do **not** dump raw tool logs or huge diffs.

Collect:

- **Goal** — what the user is trying to ship or decide
- **Current state** — done vs in progress vs blocked
- **Decisions** — with brief rationale; note rejected options when important
- **Changed / touched paths** — from **`git status`** and **`git diff --stat`** when in a git repo (if not git, list paths mentioned in chat)
- **Commands** — only high-signal commands the next session should rerun
- **Blockers / open questions**
- **Next steps** — ordered, actionable (3–7 items)
- **Do not redo** — dead ends already tried

**Secrets:** User is responsible for review before sharing; still avoid pasting obvious `.env` values or tokens if they appeared in chat.

## Reference documents (tiered discovery)

Cap **~15** entries. Prefer **absolute paths** from workspace root. **Rank paths that appear in both § Chat transcript (24h) and git/session higher.**

1. **Chat transcript (24h):** paths and docs surfaced in § Chat transcript — primary source for “what mattered in this window.”
2. **Git:** staged/unstaged/untracked paths; prioritize `docs/`, `specs/`, `*plan*.md`, `AGENTS.md`, `README.md`, `.cursor/plans/`, `seed_grow/plans/`.
3. **Repo anchors:** `AGENTS.md`, `docs/PRODUCT.md`, `docs/ARCHITECTURE.md`, `GLOSSARY.md` when present.
4. **Visible session:** every doc/path the user **@-mentioned** or that you cited as source of truth.
5. **Search (if needed):** ripgrep or glob for `**/REFACTOR*.md`, `**/TODO*.md`, `docs/specs/**` tied to the task.

For each reference, **one line:** why the next chat should open it.

## Handoff document template

Write the file and **`latest.md`** using this structure (fill completely; use `N/A` only with reason):

```markdown
# New-chat handoff

**Generated:** <ISO8601 or same as filename timestamp>
**Repo:** <path or name>
**Branch:** <git branch or N/A>
**Handoff file:** <relative path to this file>

## Handoff source

| Field | Value |
|-------|-------|
| Chat title | <Cursor chat title or inferred label> |
| Transcript ID | <UUID from agent-transcripts path, or N/A> |
| Transcript path | <absolute path to .jsonl if known, else N/A> |
| Saved handoff | `<tmp/handoff/HAND_OFF_…md>` (this file) |
| Generated | <same as top Generated> |

**Topic (1–2 sentences):** <plain summary for `/resume-from-hand-off-cur` — what this window was about>

## TL;DR

<2–4 sentences>

## Goal

## Current state

## Decisions

- <decision> — <why>

## Reference documents

| Path | Why read |
|------|----------|
| `<absolute or repo-root-relative path>` | <one line> |

## Files touched (session)

- `<path>` — <created|modified|discussed>

## Commands to reproduce

```bash
<only if applicable>
```

## Next steps

1. ...
2. ...

## Do not redo

- ...

## Resume prompt (new Agent chat)

> Run **`/resume-from-hand-off-cur`** (or **`/resume-from-hand-off-cur tmp/handoff/HAND_OFF_….md`**). Then say which **Next step** to run.
```

## Procedure (checklist)

1. Run **`/hand-off-cur`** scope: confirm user wants save now.
2. Resolve **chat tab title** (§ Filename — ask **“Tab title?”** if missing; do not write handoff files until answered).
3. `mkdir -p tmp/handoff`
4. Update **`.gitignore`** if `tmp/handoff/` not ignored.
5. **Read § Chat transcript (24h)** for the current window; then gather git state and tiered docs (§ Reference documents).
6. Derive **TitleKey** from **tab title** (§ Filename); fill **§ Handoff source** (same title, transcript ID/path from `transcript_location` or JSONL path).
7. Write **`tmp/handoff/HAND_OFF_<timestamp>_<TitleKey>.md`**
8. Write **`tmp/handoff/latest.md`** with **identical** content.
9. Reply with: file paths, **Resume prompt** excerpt, and the full **New-chat handoff** block in a single copyable markdown section.

## Install (other machines / all projects)

Copy this folder to personal skills:

```bash
mkdir -p ~/.cursor/skills
cp -R /path/to/any-repo/.cursor/skills/hand-off-cur ~/.cursor/skills/hand-off-cur
```

Restart or new Agent chat; invoke **`/hand-off-cur`**. See **`INSTALL.md`** in this directory.

## Limitations

- If **`transcript_location`** is missing and no JSONL can be matched to this chat, note **`Transcript: unavailable`** in the handoff and rely on visible context + git (do not skip attempting `~/.cursor/projects/*/agent-transcripts/`).
- Very long transcripts: **24h filter + grep** only; never attach full JSONL to the handoff.
- Generic tab titles (`New Chat`) produce weak **TitleKey**; timestamp still uniquifies filenames — user may rename the tab before **`/hand-off-cur`**.
