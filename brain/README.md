# Brain-profiles

`brain/` holds exactly two **brain-profiles**. Each one is a separate LLM Wiki (Nashsu) project root with its own `purpose.md`, `schema.md`, `raw/sources/`, `wiki/`, `manifests/`, and local `.llm-wiki/` state.

| Profile | Path | Use |
|---------|------|-----|
| `retail` (default) | `brain/retail/` | Fridges R Us (FRU) US aftersales brain: fridge manuals + ticket answer bundle (`retail_answer.v1`) |
| `personal` | `brain/personal/` | Personal second brain (notes, uploads, web clips) |

Only these files are shared at this level: `.gitignore` and this `README.md`.

## Switching

One profile is active at a time:

1. `BRAIN_PROFILE=retail|personal` (env) wins.
2. Else `active_brain_profile:` in `config/brain-stack.yaml`.
3. Else `retail`.

Scripts derive `BRAIN_ROOT` (`brain/<profile>`) and the wiki vault (`brain/<profile>/wiki`) from it:

```bash
eval "$(python3.12 scripts/brain/brain_stack.py profile-env)"
echo "$BRAIN_PROFILE -> $BRAIN_ROOT"
```

Desktop apps are switched by hand: open the matching folder as the LLM Wiki project and the matching `wiki/` folder as the Obsidian vault.
