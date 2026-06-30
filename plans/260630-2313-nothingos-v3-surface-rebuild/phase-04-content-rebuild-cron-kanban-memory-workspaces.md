---
phase: 4
title: "Content rebuild: Cron, Kanban, Memory, Workspaces"
status: completed
priority: P1
dependencies: [1, 2, 3]
---

# Phase 4: Content rebuild — Cron, Kanban, Memory, Workspaces

## Overview
Rebuild the four routes the V2 brief criticized most (§4.1, 4.3, 4.4, 4.5). These need real content/anatomy changes, not just primitive application. Each renders via JS templates in `panels.js`/`sessions.js`/`workspace.js` — change templates + CSS, keep `#panel*` ids and `switchPanel` intact.

## Requirements
- Functional: each route shows the metadata the brief requires; route data loading (`loadCrons`, `loadKanban`, memory load, workspace browser) unchanged.
- Non-functional: red as signal only; touch rows 48–56px; no horizontal overflow at 390px (full mobile pass is phase 6, but build mobile-aware here).

## Architecture
- **Cron/Tasks** (`#panelTasks`, `#cronList`; renderers in `panels.js`/`sessions.js`): LED status (`● ACTIVE`) not green pill; job card shows next run / last run / cron expr / env / failures (`.n-technical`); numeric/dot job glyph replacing robot emoji; use empty space for a schedule timeline. (Brief §4.3)
- **Kanban** (`#panelKanban`, `.kanban-filter-stack`, `#kanbanList`): collapse advanced filters (assignee/tenant/archived/mine/bulk) into a phase-1 `.os-sheet`; show cards in first viewport; group by status lanes; red only for dispatcher/blocked; fix new-task-row overflow. (Brief §4.4)
- **Memory** (`#panelMemory` + `#mainMemory` reader): neutral code chips by default (kill red overload); readable body 18–22px mobile; render standalone `§` as `.os-divider`; `overflow-wrap:anywhere` + `box-decoration-break:clone` for long paths; clarify Memory(module)/MEMORY.md(file)/heading hierarchy. (Brief §4.5)
- **Workspaces/Spaces** (`#panelWorkspaces` + `.rightpanel` browser; `workspace.js`): tactile 48–56px `.os-row` file rows; breadcrumb/path chip; `Files`/`Artifacts` as `.os-segmented` (equal zones); mobile chevrons instead of tiny disclosure triangles. (Brief §4.1)

## Related Code Files
- Modify: `static/panels.js` — cron + kanban + memory render templates.
- Modify: `static/sessions.js` — if cron/session card rendering lives here (verify which file owns `#cronList` rows).
- Modify: `static/workspace.js` — file-row + breadcrumb + segment rendering.
- Modify: `static/index.html` — static markup for kanban filter stack → sheet trigger, memory reader header, workspace segment (keep ids).
- Modify: `static/style.css` (V3 block) — per-route styles built on phase-1 primitives.

## Implementation Steps
1. For each route: grep the render function that owns its list/cards; map the data already available (no new API).
2. **Cron**: rebuild job card template (LED + schedule metadata + dot/numeric glyph); add timeline header in empty space; remove emoji + green pill.
3. **Kanban**: move advanced filters into `.os-sheet` triggered by a `[Tune]` control; render status lanes; fix overflow on the new-task row; restrict red to dispatcher/blocked.
4. **Memory**: set code chips neutral default; bump reader body size; map `§` → `.os-divider`; add long-path wrapping; restructure header hierarchy.
5. **Workspaces**: convert file rows to `.os-row`; add breadcrumb chip; `Files/Artifacts` → `.os-segmented`; replace disclosure triangles with chevrons/open-row.
6. Verify each route loads + interacts (run cron, open kanban card, edit memory, browse workspace) with no logic regression.

## Success Criteria
- [ ] Cron cards show next/last/cron/env; LED status; no emoji; no generic green pill.
- [ ] Kanban: advanced filters collapsed into sheet; cards visible in first viewport; lanes grouped; no 390px overflow on new-task row.
- [ ] Memory: code chips neutral; body readable; `§` → dotted divider; long paths wrap; clear hierarchy.
- [ ] Workspaces: 48–56px tactile rows; breadcrumb chip; balanced Files/Artifacts segment.
- [ ] All four routes load + function unchanged; `npm run lint:runtime` + `node --check` pass; console = 0 errors.

## Risk Assessment
- **Renderer ownership ambiguity** (panels.js vs sessions.js vs workspace.js) → confirm owning file by grep before editing each route.
- **Kanban filter logic coupling** → moving filters into a sheet must keep the same input ids/handlers (`#kanbanAssigneeFilter`, `#kanbanOnlyMine`, etc.) wired to `loadKanban`.
- **Memory markdown renderer** → chip styling is CSS; do not alter the markdown→HTML pipeline logic.
