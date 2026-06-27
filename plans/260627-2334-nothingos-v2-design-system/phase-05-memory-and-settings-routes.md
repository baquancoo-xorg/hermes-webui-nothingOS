---
phase: 5
title: "Memory and Settings Routes"
status: completed
priority: P1
dependencies: [3]
---

# Phase 5: Memory and Settings Routes

## Overview
Migrate Memory and Settings, the two routes most visibly damaged by the global bottom toolbar and red/mono overuse. This phase focuses on readability, full-token theme behavior, and calm grouped controls.

## Requirements
- Functional: Memory has no bottom toolbar clipping and uses readable UI sans body text.
- Functional: code/path chips neutral by default and wrap safely.
- Functional: Settings Appearance uses grouped rows/switches and true full-page light/dark token changes.
- Functional: accent copy is either backed by a real control or removed.
- Non-functional: preserve existing settings persistence keys and memory API behavior.

## Architecture
Memory should behave like a reader/editor route, not a card stack hidden behind global controls. Settings should use route surface sections with grouped control rows. Keep existing settings IDs/persistence paths so `boot.js` and `panels.js` keep working.

## Related Code Files
- Modify: `static/index.html` — Memory/Settings section markup hooks if needed.
- Modify: `static/style.css` — Memory typography, code chip neutrality, long path wrapping, Settings grouped rows.
- Modify: `static/panels.js` — Settings rendering/behavior only if existing DOM needs route hooks.
- Modify: `static/boot.js` — theme/font size apply path only if required.
- Tests: `tests/test_issue3506_memory_and_watcher.py`, `tests/test_memory_skill_badge.py`, `tests/test_issue2462_theme_i18n.py`, `tests/test_theme_color_meta_bridge.py`.
- Update after code: `.claude/features/nothingos-v2-route-surfaces.md`

## Tests Before
1. Add/adjust tests for:
   - Memory route has neutral inline code/chip styling hooks.
   - Settings theme toggle still writes/reads expected localStorage key.
   - Appearance copy does not mention unsupported accent options.
2. Run focused tests:
   ```bash
   ./scripts/test.sh tests/test_issue2462_theme_i18n.py tests/test_theme_color_meta_bridge.py -q
   ```

## Refactor
1. Memory:
   - remove dependency on any global bottom toolbar.
   - set body text to UI sans at readable mobile size.
   - make code/path chips neutral and wrap using `overflow-wrap:anywhere` and `box-decoration-break:clone` where useful.
   - convert standalone section marker `§` to dotted divider if rendering path supports it safely.
   - clarify hierarchy: Memory route → MEMORY.md file → document heading.
2. Settings:
   - replace checkbox-card feel with grouped rows and right-aligned switches.
   - make theme picker visibly affect page tokens.
   - change font size control to 2x2 grid or simpler balanced selector.
   - move unrelated Workspace behavior copy out of Appearance if present, or label it clearly.
   - add accent section only if existing settings support it; otherwise remove misleading copy.

## Tests After
- Memory/settings focused tests pass.
- Theme/static tests pass.
- Manual 390px spot check: Memory/Settings content not hidden by fixed bar; no horizontal overflow.

## Regression Gate
```bash
./scripts/test.sh tests/test_issue2462_theme_i18n.py tests/test_theme_color_meta_bridge.py tests/test_issue3506_memory_and_watcher.py tests/test_memory_skill_badge.py -q
./scripts/test.sh tests/test_static_js_runtime_lint.py tests/test_static_js_scope_undef.py -q
```

## Success Criteria
- [x] Memory content is not obscured by fixed bottom controls.
- [x] Memory body text uses readable UI sans sizing.
- [x] Memory code/path chips are neutral and wrap long paths.
- [x] Settings uses grouped rows/switches, not generic nested card overload.
- [x] Light/Dark setting changes full page tokens.
- [x] Accent copy is truthful.
- [x] Existing memory/settings persistence still works.
- [x] Feature doc updated after implementation.

## Risk Assessment
- Risk: changing memory renderer affects markdown safety. Mitigation: prefer CSS for `§` divider unless renderer already supports safe transform.
- Risk: settings markup changes break localStorage wiring. Mitigation: preserve IDs and existing event handlers.
- Risk: light mode partial regressions. Mitigation: Phase 3 token tests + Phase 7 browser QA.
