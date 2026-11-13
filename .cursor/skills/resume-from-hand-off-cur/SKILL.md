---
name: resume-from-hand-off-cur
description: >-
  Explicit /resume-from-hand-off-cur only. Load a handoff written by hand-off-cur
  (default tmp/handoff/latest.md), reply with concise source chat + topic, then wait
  for the user to pick a next step. Use when the user types /resume-from-hand-off-cur.
disable-model-invocation: true
---

# resume-from-hand-off-cur — load handoff in a new Agent chat

Companion to **`hand-off-cur`**. Use in a **new** chat after a handoff was saved. Trigger only via **`/resume-from-hand-off-cur`** (do not auto-apply).

## Arguments

| Input | Behavior |
|-------|----------|
| **`/resume-from-hand-off-cur`** | Load **`tmp/handoff/latest.md`** (repo root relative). |
| **`/resume-from-hand-off-cur tmp/handoff/HAND_OFF_….md`** | Load that file instead. |
| **`@tmp/handoff/latest.md`** plus slash | Same as default if path matches. |

If the file is missing, report clearly and list **`tmp/handoff/HAND_OFF_*.md`** if any exist (newest first). **Do not** invent handoff content.

## Procedure

1. **Resolve path** (default `tmp/handoff/latest.md`); **Read** the file.
2. Parse **`## Handoff source`** (table + **Topic (1–2 sentences)**). Fallback if old handoff lacks it: **Chat title** = N/A, **Transcript ID** = N/A, topic from **TL;DR** or **Goal** (first 2 sentences max).
3. **Reply once** — concise, fixed shape (below). **Do not** start **Next steps**, read reference docs, or code until the user asks (e.g. “go”, “step 1”, “continue P5”).
4. End with one line: *Say which **Next step** to run, or `@` a reference doc.*

## Required reply shape (keep short)

```markdown
**Handoff loaded:** `<path>`

**From:** <Chat title> · **Transcript ID:** `<uuid or N/A>`

**Was about:** <Topic 1–2 sentences from Handoff source, or TL;DR fallback>

**Next:** <first item from Next steps list, one line only> — waiting for your go-ahead.
```

Do **not** dump the full handoff file. Do **not** run git or transcript mining on resume unless the user requests continuation.

## When user continues

After the user names a step or says to proceed:

1. Re-read **Reference documents** and **Do not redo** from the handoff file.
2. Open the listed docs needed for that step.
3. Run **`git status`** / **`git branch`** briefly if the handoff is code work.
4. Execute the requested **Next step** only.

## Install

Copy with **`hand-off-cur`**:

```bash
mkdir -p ~/.cursor/skills
cp -R /path/to/repo/.cursor/skills/resume-from-hand-off-cur ~/.cursor/skills/resume-from-hand-off-cur
```

See **`hand-off-cur/INSTALL.md`**.
