<h1 id="install-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Install hand-off-cur (all projects)</h1>

<h2 id="install-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Copy skill](#install-copy) — personal `~/.cursor/skills/`
2. [Use](#install-use) — slash command and outputs
3. [Gitignore](#install-gitignore) — per-repo `tmp/handoff/`

---

<h2 id="install-copy" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Copy skill</h2>

From this repository:

```bash
mkdir -p ~/.cursor/skills
cp -R "$(git rev-parse --show-toplevel)/.cursor/skills/hand-off-cur" ~/.cursor/skills/hand-off-cur
```

Or copy `.cursor/skills/hand-off-cur/` from any checkout that contains the skill.

<h2 id="install-use" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Use</h2>

**Save (old chat):**

1. **`/hand-off-cur`**
2. Agent reads **24h transcript**, writes **`tmp/handoff/HAND_OFF_<YYYYMMDD-HHmmss>_<TitleKey>.md`** + **`tmp/handoff/latest.md`** (includes **Handoff source** metadata).

**Resume (new chat):**

1. **`/resume-from-hand-off-cur`** — loads **`latest.md`**, short “from / about” reply, waits for you.
2. Optional: **`/resume-from-hand-off-cur tmp/handoff/HAND_OFF_….md`**
3. Say which **Next step** to run (or install **`resume-from-hand-off-cur`** from `.cursor/skills/` — see its **INSTALL.md**).

<h2 id="install-gitignore" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Gitignore</h2>

The skill asks the agent to add **`tmp/handoff/`** to `.gitignore` when missing. Handoffs stay local unless you commit them on purpose.
