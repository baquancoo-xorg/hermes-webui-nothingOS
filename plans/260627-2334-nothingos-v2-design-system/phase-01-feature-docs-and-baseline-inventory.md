---
phase: 1
title: "Feature Docs and Baseline Inventory"
status: completed
priority: P1
dependencies: []
---

# Phase 1: Feature Docs and Baseline Inventory

## Overview
Create the persistent feature documentation required by project workflow and capture the current shell/route contracts before code moves. This phase prevents accidental JS/DOM/API breakage in later phases.

## Requirements
- Functional: document current NothingOS V2 target and route ownership rules under `.claude/features/`.
- Functional: inventory selectors, IDs, API fields, and test files used by shell, quick tray, Workspace, Chat, Jobs, Kanban, Memory, Settings.
- Non-functional: no runtime behavior change except tests/docs if needed.

## Architecture
This phase treats docs and tests as the safety harness. It should map existing DOM IDs/classes to V2 wrappers rather than inventing final code. Cron/job metadata must be verified from actual API payloads before Phase 6 promises labels.

## Related Code Files
- Create: `.claude/features/nothingos-v2-route-shell.md`
- Create: `.claude/features/nothingos-v2-route-surfaces.md`
- Modify: `.claude/features/*` index/table if present; otherwise create minimal feature index if project convention exists.
- Read: `static/index.html`, `static/style.css`, `static/tokens.css`, `static/os-widgets.js`, `static/boot.js`, `static/panels.js`, `static/workspace.js`, `static/sessions.js`
- Read: `tests/test_static_js_runtime_lint.py`, `tests/test_static_js_scope_undef.py`, focused route UI tests listed in `plan.md`

## Tests Before
1. Run focused static/lint tests to confirm baseline:
   ```bash
   ./scripts/test.sh tests/test_static_js_runtime_lint.py -q
   ./scripts/test.sh tests/test_static_js_scope_undef.py -q
   ```
2. Add or update a small static contract test if missing for required shell hooks:
   - `#osAmbient`
   - `#osQuick` or its removal/re-scope marker
   - `.rail`, `.sidebar`, `.rightpanel`
   - route panel IDs: `#panelChat`, `#panelTasks`, `#panelKanban`, `#panelMemory`, `#panelSettings` if present

## Refactor
1. Create feature docs with:
   - current behavior
   - V2 target behavior
   - required tests/QA
   - affected files
   - how to update after implementation
2. Inventory real cron/job payload fields from tests/API code before Phase 6 implementation.
3. Note current quick tray entry points and route dependencies.
4. Identify selectors that must remain stable for JS.

## Tests After
- Static contract tests pass.
- Feature docs contain enough detail for later phases.
- No code behavior changed unless a test file was added.

## Regression Gate
```bash
./scripts/test.sh tests/test_static_js_runtime_lint.py tests/test_static_js_scope_undef.py -q
```

## Success Criteria
- [ ] Feature docs exist and describe V2 shell/routes.
- [ ] Required DOM IDs/selectors inventory recorded in feature docs or phase notes.
- [ ] Cron/job metadata source verified or limitation documented.
- [ ] Baseline static tests pass before shell refactor.
- [ ] No product behavior changed in this phase.

## Risk Assessment
- Risk: feature docs become generic noise. Mitigation: document only V2 contracts needed by implementation.
- Risk: tests assert brittle markup. Mitigation: assert stable hooks and behavior, not exact nested HTML.
