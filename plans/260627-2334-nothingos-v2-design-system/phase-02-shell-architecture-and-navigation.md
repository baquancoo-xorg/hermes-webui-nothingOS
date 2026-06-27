---
phase: 2
title: "Shell Architecture and Navigation"
status: completed
priority: P1
dependencies: [1]
---

# Phase 2: Shell Architecture and Navigation

## Overview
Convert the current V1 shell from persistent rail/sidebar/rightpanel/global quick tray into a route-owned responsive shell. This phase fixes the root mobile architecture before route polish.

## Requirements
- Functional: mobile `<768px` has no persistent full-height rail, clipped side panel, or global quick tray.
- Functional: desktop keeps fast navigation and existing route access.
- Functional: preserve existing route panel IDs and JS entry points.
- Non-functional: no backend API changes; vanilla JS only.

## Architecture
Add a light `RouteShell` layer through CSS classes/data attributes around existing DOM. Do not rename IDs used by `boot.js`, `panels.js`, `workspace.js`, `sessions.js`, or `messages.js`. Use CSS and small JS state helpers to decide whether route controls appear as header actions, drawer, bottom sheet, or route dock.

Responsive tiers:

| Tier | Contract |
|---|---|
| Desktop >=1024px | Compact rail visible; route content primary; contextual panel allowed. |
| Tablet 768-1023px | Launcher/compact nav; route surface full; panels open intentionally. |
| Mobile <768px | Full-width route surface; no persistent rail/right split; max two visible header actions. |

## Related Code Files
- Modify: `static/index.html` — add route-shell wrappers/classes, remove/re-scope global quick tray markup.
- Modify: `static/style.css` — responsive shell tiers, no-overflow rules, safe-area handling.
- Modify: `static/boot.js` — route switching / drawer state / mobile launcher behavior.
- Modify: `static/os-widgets.js` — keep ambient status; remove or route-scope quick tray.
- Modify: `static/workspace.js` — align rightpanel open/close behavior with route shell.
- Modify/Create tests: shell static contract and browser smoke tests.
- Update after code: `.claude/features/nothingos-v2-route-shell.md`

## Tests Before
1. Add failing static tests for mobile shell contracts where practical:
   - quick tray is not global/persistent on all routes.
   - route panel IDs still exist.
   - mobile-only controls have accessible labels.
2. Run:
   ```bash
   ./scripts/test.sh tests/test_static_js_runtime_lint.py tests/test_static_js_scope_undef.py -q
   ```

## Refactor
1. Introduce shell class names such as `.route-shell`, `.route-header`, `.route-surface`, `.route-dock`, `.bottom-sheet` only where reused.
2. Re-scope `#osQuick`:
   - remove from global flow, or
   - keep dormant shell for backward compatibility but render route-specific docks only.
3. Collapse/hide rail and right panel on mobile unless intentionally opened.
4. Move route state into top header/ambient strip instead of bottom cards.
5. Ensure touch target rules for launcher/drawer controls.

## Tests After
- Static JS checks pass.
- Shell contract tests pass.
- Manual or automated 390px smoke shows no horizontal overflow on at least Chat and Settings before route-specific phases.

## Regression Gate
```bash
./scripts/test.sh tests/test_static_js_runtime_lint.py tests/test_static_js_scope_undef.py -q
python3 -m py_compile server.py
```

## Success Criteria
- [ ] Mobile shell has no persistent rail below tablet width.
- [ ] Mobile shell has no clipped right panel/split pane.
- [ ] Global bottom quick tray is removed or inert outside route-specific docks.
- [ ] Header exposes max two visible mobile actions per route surface.
- [ ] Existing JS route switching still works.
- [ ] Feature doc updated after implementation.

## Risk Assessment
- Risk: hiding old panels breaks route access. Mitigation: keep route switching IDs/hooks; use drawers instead of deleting content.
- Risk: desktop usability regresses. Mitigation: desktop tier keeps compact rail and optional panels.
- Risk: CSS cascade leaves old quick tray visible. Mitigation: add explicit route-scope tests/selectors.
