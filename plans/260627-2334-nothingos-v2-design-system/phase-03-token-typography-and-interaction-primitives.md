---
phase: 3
title: "Token Typography and Interaction Primitives"
status: completed
priority: P1
dependencies: [2]
---

# Phase 3: Token Typography and Interaction Primitives

## Overview
Reset NothingOS V2 visual language at token and primitive level: red as signal, dot/display as accent, mono only metadata, and tactile LED/dot interactions. This prevents route work from becoming one-off CSS patches.

## Requirements
- Functional: full-page light/dark token flip remains working.
- Functional: red is reserved for active/critical/destructive/primary states.
- Functional: code chips are neutral by default.
- Functional: reusable primitives exist only where multiple routes need them.
- Non-functional: no proprietary Nothing font/logo/assets.

## Architecture
Keep `static/tokens.css` as source of truth for V2 tokens. Add small component classes to `static/style.css` only when they are reused across at least two routes. Avoid a large JS component system; primitives are DOM/CSS conventions with optional small helper functions.

Candidate primitives:

| Primitive | Use | Keep if reused by |
|---|---|---|
| `LedStatus` | idle/active/error/blocked dots/labels | Jobs, Kanban, ambient strip |
| `OsSegmentedControl` | balanced route tabs/chips | Workspace, Chat filters, Settings |
| `TactileButton` | mechanical press state | primary controls, route docks |
| `BottomSheet` | mobile secondary controls | Kanban filters, Workspace more |
| `TechMeta` | mono metadata rows | paths, cron, model, branch |
| `DotDisplayLabel` | short identity/status label | app mark, headers, counters |

## Related Code Files
- Modify: `static/tokens.css` — V2 token aliases, contrast, red calibration, type aliases.
- Modify: `static/style.css` — primitives and global chip/code neutrality.
- Modify: `static/boot.js` / `static/panels.js` only if settings/theme controls need minor class state updates.
- Modify tests: `tests/test_uiux_docs_theme_contract.py`, `tests/test_theme_color_meta_bridge.py`, `tests/test_issue2462_theme_i18n.py`, static UI tests where appropriate.
- Update after code: `.claude/features/nothingos-v2-route-shell.md`, `.claude/features/nothingos-v2-route-surfaces.md`

## Tests Before
1. Add/adjust tests asserting:
   - light/dark pre-paint still sets root class and meta color.
   - default inline code/chips do not use red-only styling.
   - theme selector changes full root tokens.
2. Run focused theme/static tests:
   ```bash
   ./scripts/test.sh tests/test_theme_color_meta_bridge.py tests/test_issue2462_theme_i18n.py tests/test_uiux_docs_theme_contract.py -q
   ```

## Refactor
1. Add V2 token aliases without deleting old variables still used by legacy CSS.
2. Normalize red variables: primary red, red soft, red line, critical/error aliases.
3. Define type tiers in tokens:
   - UI sans for labels/body/control text.
   - display/dot class for short identity/status only.
   - mono metadata class for paths/model/cron/time.
4. Neutralize code chip defaults globally, then re-enable red only through semantic classes.
5. Add LED/dot/segmented/tactile classes where later route phases will reuse them.

## Tests After
- Theme/static tests pass.
- No JS syntax/scope regressions.
- Manual spot-check light/dark root token flip in browser or static DOM if browser unavailable.

## Regression Gate
```bash
./scripts/test.sh tests/test_theme_color_meta_bridge.py tests/test_issue2462_theme_i18n.py tests/test_uiux_docs_theme_contract.py -q
./scripts/test.sh tests/test_static_js_runtime_lint.py tests/test_static_js_scope_undef.py -q
```

## Success Criteria
- [x] V2 tokens support dark and light full-page surfaces.
- [x] Dot/display and mono usage rules documented in code or feature docs.
- [x] Code chips neutral by default.
- [x] Reusable primitives are present but not over-abstracted.
- [x] Red usage can be applied semantically by route phases.
- [x] Feature docs updated after implementation.

## Risk Assessment
- Risk: token rename breaks legacy selectors. Mitigation: add aliases first; delete old variables only if proven unused.
- Risk: primitives become framework-like abstraction. Mitigation: CSS classes + tiny helpers only, no component registry.
- Risk: contrast regressions in light mode. Mitigation: test theme contract and browser QA in Phase 7.
