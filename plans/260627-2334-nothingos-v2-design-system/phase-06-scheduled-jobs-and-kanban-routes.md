---
phase: 6
title: "Scheduled Jobs and Kanban Routes"
status: completed
priority: P1
dependencies: [3]
---

# Phase 6: Scheduled Jobs and Kanban Routes

## Overview
Migrate Scheduled Jobs and Kanban from generic admin/card controls to route-specific operational surfaces. Jobs should expose schedule state clearly; Kanban should show cards early and move advanced filters into secondary controls.

## Requirements
- Functional: Scheduled Jobs show visible primary `+ New Job`, LED status, and real schedule metadata from available API fields.
- Functional: no robot emoji or saturated green status pills in Jobs.
- Functional: Kanban mobile shows task cards in first viewport after compact controls.
- Functional: Kanban advanced filters move to bottom sheet/overflow on mobile.
- Functional: existing job run/pause/resume/log and Kanban create/update/dispatcher behavior remains intact.
- Non-functional: do not invent fake cron metadata if API does not provide it.

## Architecture
Use Phase 3 primitives for LED status, technical metadata, tactile buttons, and bottom sheets. Jobs may render a compact timeline only if current data supports it; otherwise show truthful next/last/cron/environment/failure equivalents. Kanban keeps underlying data model and actions; only presentation/control hierarchy changes.

## Related Code Files
- Modify: `static/index.html` — panel hooks for Jobs/Kanban actions and filter sheet if needed.
- Modify: `static/style.css` — Jobs card anatomy, LED status, Kanban lanes/filter sheet/mobile layout.
- Modify: `static/panels.js` — Jobs/Kanban render functions and filter sheet interactions.
- Tests: `tests/test_cron_refresh_button_835.py`, `tests/test_issue2289_cron_detail_expansion.py`, `tests/test_cron_model_provider_picker.py`, `tests/test_kanban_ui_static.py`, `tests/test_kanban_board_ui.py`, `tests/test_kanban_view_toggle.py`.
- Update after code: `.claude/features/nothingos-v2-route-surfaces.md`

## Tests Before
1. Verify real job fields from API/tests before labels are planned in code.
2. Add/adjust tests for:
   - Jobs render schedule metadata when present.
   - Jobs status uses semantic LED class, not generic green pill/emoji.
   - Kanban mobile has filter summary/tune control rather than full filter stack.
   - Existing action buttons remain present and accessible.
3. Run focused tests:
   ```bash
   ./scripts/test.sh tests/test_kanban_ui_static.py tests/test_kanban_board_ui.py tests/test_kanban_view_toggle.py -q
   ./scripts/test.sh tests/test_cron_refresh_button_835.py tests/test_issue2289_cron_detail_expansion.py -q
   ```

## Refactor
1. Scheduled Jobs:
   - promote `+ New Job` to clear primary action.
   - replace emoji/index visuals with numeric index or monochrome glyph.
   - render `LedStatus` for active/paused/error/needs-attention.
   - show next run, last run, cron/env/failure equivalents using real fields only.
   - use empty space for activity diagnostics/timeline if data exists.
2. Kanban:
   - collapse assignee/tenant/archive/mine/bulk/preview controls into summary + bottom sheet/overflow on mobile.
   - show task cards earlier in viewport.
   - group mobile cards by status lanes.
   - reserve red for dispatcher/blocked/critical states.
   - keep dispatcher and bulk actions accessible but secondary.

## Tests After
- Cron and Kanban focused tests pass.
- Static JS tests pass.
- Manual 390px spot check: cards visible early, no horizontal overflow, controls accessible.

## Regression Gate
```bash
./scripts/test.sh tests/test_kanban_ui_static.py tests/test_kanban_board_ui.py tests/test_kanban_view_toggle.py -q
./scripts/test.sh tests/test_cron_refresh_button_835.py tests/test_issue2289_cron_detail_expansion.py tests/test_cron_model_provider_picker.py -q
./scripts/test.sh tests/test_static_js_runtime_lint.py tests/test_static_js_scope_undef.py -q
```

## Success Criteria
- [x] Jobs primary `+ New Job` is visible and clear.
- [x] Jobs status uses LED language, not generic green pill.
- [x] Jobs cards show real schedule metadata or documented equivalent.
- [x] No robot emoji remains in Jobs route presentation.
- [x] Kanban task cards appear in first mobile viewport after compact controls.
- [x] Kanban advanced filters are in sheet/overflow on mobile.
- [x] Kanban status lanes are clear on mobile.
- [x] Existing Jobs/Kanban actions still work.
- [x] Feature doc updated after implementation.

## Risk Assessment
- Risk: API lacks next/last run fields. Mitigation: use cron expression and available run history/failure fields; document limitation.
- Risk: hiding filters harms power users. Mitigation: summary + one-tap bottom sheet keeps filters accessible.
- Risk: Kanban action regressions. Mitigation: preserve IDs/events; run focused Kanban tests.
