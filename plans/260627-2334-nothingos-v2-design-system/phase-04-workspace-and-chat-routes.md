---
phase: 4
title: "Workspace and Chat Routes"
status: completed
priority: P1
dependencies: [3]
---

# Phase 4: Workspace and Chat Routes

## Overview
Migrate the two most visible workflows — Workspace and Chat — onto the V2 route-shell patterns. Workspace becomes a full-width mobile file surface; Chat treats the composer as the command surface and removes desktop residue from mobile conversation navigation.

## Requirements
- Functional: Workspace mobile shows full-width file list, route dock only there, and no clipped chat/preview side panel.
- Functional: Chat mobile has no persistent left rail, no fake close `X` on primary page, normalized filters, and selected row max two red cues.
- Functional: keep file operations, session list, search, composer, upload, and stream behavior intact.
- Non-functional: no backend changes.

## Architecture
Reuse Phase 2 shell and Phase 3 primitives. Workspace route may use a route-specific dock (`Search / New / Upload / More`). Chat must not use a global bottom dock; composer remains the command surface. Conversation list may be a full page or drawer depending on existing panel structure.

## Related Code Files
- Modify: `static/index.html` — Workspace/Chat route header/dock/sheet hooks if required.
- Modify: `static/style.css` — Workspace rows, Chat list/filter/selected-state styles, mobile route layout.
- Modify: `static/workspace.js` — rightpanel/drawer behavior and Workspace dock actions.
- Modify: `static/sessions.js` — Chat list selected-state/filter classes if needed.
- Modify: `static/messages.js` — only if composer/status needs class hooks; preserve stream behavior.
- Tests: `tests/test_session_static_assets.py`, `tests/test_project_chip_ui.py`, `tests/test_webui_surface_context.py`, workspace static tests if available.
- Update after code: `.claude/features/nothingos-v2-route-surfaces.md`

## Tests Before
1. Add/adjust static tests for Workspace/Chat DOM contracts:
   - Workspace route can open files without clipped panel assumptions.
   - Chat selected row uses semantic selected hook, not multiple red-only classes.
   - Composer controls still exist and are not moved into global dock.
2. Run focused tests:
   ```bash
   ./scripts/test.sh tests/test_session_static_assets.py tests/test_webui_surface_context.py -q
   ```

## Refactor
1. Workspace:
   - make mobile file surface full-width.
   - compress branch/delta/idle/model into ambient/header meta.
   - add route dock only for Workspace if it improves action access.
   - keep preview as drawer/sheet, not clipped side pane.
   - improve touch target rows and path wrapping.
2. Chat:
   - convert conversation list mobile to full-page/drawer model.
   - remove fake close button from full-page context.
   - normalize filter chips through `OsSegmentedControl` style.
   - limit selected row to one or two red cues.
   - preserve message composer and streaming behavior.

## Tests After
- Workspace and Chat static tests pass.
- JS lint/scope tests pass.
- Manual 390px spot check: no horizontal overflow, no clipped side panel, composer usable.

## Regression Gate
```bash
./scripts/test.sh tests/test_session_static_assets.py tests/test_webui_surface_context.py -q
./scripts/test.sh tests/test_static_js_runtime_lint.py tests/test_static_js_scope_undef.py -q
```

## Success Criteria
- [x] Workspace is full-width on mobile.
- [x] Workspace route dock exists only for Workspace or is intentionally omitted.
- [x] Workspace preview/rightpanel does not clip the mobile viewport.
- [x] Chat mobile has no persistent rail and no fake close `X` on primary page.
- [x] Chat filters use normalized chip/segmented styling.
- [x] Chat selected row uses max two red cues.
- [x] Existing chat/file/session behavior still works.
- [x] Feature doc updated after implementation.

## Risk Assessment
- Risk: Workspace drawer changes break file preview. Mitigation: preserve `openWorkspacePanel`, `showPreview`, and relevant IDs.
- Risk: Chat list changes break session CRUD. Mitigation: do not rename session item data attributes; run session static tests.
- Risk: route dock duplicates composer. Mitigation: dock only Workspace; Chat composer remains command surface.
