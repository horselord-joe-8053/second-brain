<h1 id="mod-desktop-install" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Module: desktop-install</h1>

**When:** Spec **`HG-*`** or `<!-- module: desktop-install -->` for GUI apps (LLM Wiki, Obsidian, etc.).

**Agent must not** silently install privileged software. Run:

```bash
bash bootstrap/modules/desktop-install/scripts/detect-host-os.sh
```

Then give the human **OS-specific** steps (Homebrew cask, `.dmg`, `.AppImage`,/winget). Record completion under **`## Decisions`** or the human-gate template.

| OS | Pattern |
|----|---------|
| **darwin** | `brew install --cask …` or official `.dmg` + drag to Applications |
| **linux** | distro package, AppImage, or vendor tarball |
| **windows** | winget / official installer; note WSL cannot host macOS GUI apps |

For Second Brain: LLM Wiki and Obsidian are **human-installed** on the Mac host; Hermes may be Docker or native per plan.
