<h1 id="resume-install" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Install resume-from-hand-off-cur</h1>

Pair with **`hand-off-cur`**. Copy both folders to **`~/.cursor/skills/`**.

```bash
mkdir -p ~/.cursor/skills
REPO="$(git rev-parse --show-toplevel)"
cp -R "$REPO/.cursor/skills/hand-off-cur" ~/.cursor/skills/
cp -R "$REPO/.cursor/skills/resume-from-hand-off-cur" ~/.cursor/skills/
```

**New chat:** **`/resume-from-hand-off-cur`** or **`/resume-from-hand-off-cur tmp/handoff/HAND_OFF_….md`**
