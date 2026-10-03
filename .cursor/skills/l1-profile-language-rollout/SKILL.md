---
name: l1-profile-language-rollout
description: >-
  Add a new learner profile UI language (L1) to portuguese-learn: register BCP-47
  tag, i18n chrome catalog, content_gloss seeds, bootstrap, tests, matrix sign-off.
  Use when the user runs aciubtdd on completed/REFACTOR_L1_INTERNATIONALIZATION.md with a
  TARGET_LANG, or asks to add a profile language, locale, or L1 gloss for es-MX/ko/pt-BR-style rollout.
---

# L1 profile language rollout (portuguese-learn)

## When to use

- User invokes `aciubtdd cursor_gen/refactor_plans/completed/REFACTOR_L1_INTERNATIONALIZATION.md {BCP-47}`
- User asks to add a new Profile display language with knowledge glosses and UI chrome

## Before you start

1. Read the **lang registry** in the hub plan — confirm `{TARGET}` row exists or add one.
2. Set `REFERENCE_LANG=zh-Hans` (proved wiring); copy patterns from zh seeds and `zhHans.ts`.
3. Do **not** duplicate URL inventory — routes live in `docs/assets/ASSET_L1_LEARNER_SURFACE_URLS.md`.
4. Update i18n **status only** in `REFACTOR_L1_LOCALE_COMPLETENESS_MATRIX.md` at sign-off.

## Three axes (do not conflate)

| Axis | Mechanism | Owns |
|------|-----------|------|
| **Row gloss (Type A)** | `content_gloss` EAV + API resolver | Meaning, Translation, Note, Hint in table cells |
| **UI chrome (Type B)** | `apps/web/src/i18n/{lang}.ts` + `*ChromeResolve.ts` | Nav, tabs, headers, Submit, intros |
| **Target pt-BR (L2)** | Grammar rows, lemmas | Never translate Portuguese cells for L1 |

## Phase 1 — Register `{TARGET}`

- [ ] Add `{TARGET}` to `SUPPORTED_UI_LANGUAGES` in `apps/api/app/services/content_gloss.py`
- [ ] Extend `UiLanguage` union + `DICTS` in `apps/web/src/i18n/index.ts` (stub dict = `enDict` until Phase 2)
- [ ] `resolveUiLanguage()` accepts `{TARGET}`
- [ ] Profile `<select>`: add option with native label
- [ ] `seed_dev_auth.py`: dev user with `{TARGET}` if needed
- [ ] Tests: `test_auth_ui_language.py`, `resolveUiLanguage.test.ts`

## Phase 2 — UI chrome (`{DICT}.ts`)

- [ ] Create `apps/web/src/i18n/{DICT}.ts` — **547 keys** parity with `I18N_KEYS` / `en.ts`
- [ ] Wire import in `i18n/index.ts`
- [ ] Extend `keys-coverage.test.ts` for new dict
- [ ] Extend `l1Chrome.test.ts` — non-English chrome for `{TARGET}` on sample suites

## Phase 3 — Row gloss seeds

Work band by band in hub plan entity inventory; mirror every `zh-Hans` row with `{TARGET}`.

- [ ] Update all relevant `*_gloss_seeds.py` modules
- [ ] Extend `test_gloss_seed_parity.py` for `{TARGET}` (same waivers as es-MX/ko/pt-BR)
- [ ] Bump `test_gloss_l1_api.py` harness key; add smoke rows with dev profile

**v1 waivers (do not block sign-off):** `verb_comp_frame`, full `verb.english_hint`, suffix-pattern `example_pt` parentheticals.

## Phase 4 — Bootstrap and runtime

```bash
python ops/local/run_bootstrap_content_gloss_sync.py
```

- [ ] Script exits 0 on DEV Postgres
- [ ] Restart API + Vite
- [ ] Manual smoke: Profile `{NATIVE_LABEL}` → suffix-patterns note in `{TARGET}` (not English)

## Phase 5 — Sign-off

- [ ] Update hub plan locale status table — mark `{TARGET}` phases `[X]`
- [ ] Update completeness matrix entity rollup columns for `{TARGET}`
- [ ] Do **not** create a second rollout plan file — single hub only

## File map

| Concern | Path |
|---------|------|
| API allowlist | `apps/api/app/services/content_gloss.py` |
| Web i18n | `apps/web/src/i18n/index.ts`, `apps/web/src/i18n/{DICT}.ts` |
| Profile | `apps/web/src/pages/ProfilePage.tsx` |
| Dev auth | `apps/api/app/db/seeds/seed_dev_auth.py` |
| Seeds | `apps/api/app/ingestion/bootstrap/*_gloss_seeds.py` |
| Parity CI | `tests/unit/test_gloss_seed_parity.py` |
| API smoke | `tests/unit/test_gloss_l1_api.py` |
| Chrome CI | `tests/e2e/unit/vitest/i18n/keys-coverage.test.ts` |

## TDD mode

- Phases 1–3: **strict-TDD** (red test → implement → green)
- Phases 4–5: **smoke-after** (ops + docs)

Follow `.cursor/rules/tdd/aciubtdd-allow-continue-iterations-until-blocked.mdc` when user passes `aciubtdd`.
