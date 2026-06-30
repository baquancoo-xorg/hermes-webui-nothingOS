---
phase: 5
title: "Apply-primitive: Settings, Skills, Profiles, Todos, Insights, Logs"
status: completed
priority: P2
dependencies: [1, 2, 3]
---

# Phase 5: Apply-primitive — secondary routes

## Overview
Bring the remaining six routes up to the design system by applying phase-1 primitives. These need less bespoke anatomy than phase 4 — mostly list-row/card/segmented/switch primitives + red discipline. Settings gets the most attention (brief §4.6).

## Requirements
- Functional: settings controls, skills list, profiles, todos, insights charts, logs all keep behavior; only presentation changes.
- Non-functional: red discipline; touch-safe; consistent typography tiers across all routes.

## Architecture
- **Settings** (`#panelSettings`/`#mainSettings`, brief §4.6): replace checkbox cards with grouped settings rows + right-aligned switches; font-size as 2×2 grid; thin red selected outline (no nested red rectangles); ensure no fixed bar overlaps content. Keep the existing single-skin appearance (no theme-picker reintroduction — prior plans removed it deliberately).
- **Skills / Profiles / Todos** (`#panelSkills`, `#panelProfiles`, `#panelTodos`): list items → `.os-row`; cards → `.os-card`; status → `.os-led`.
- **Insights** (`#panelInsights`): chart containers as `.os-surface`; labels `.n-display`/`.n-technical`; keep chart rendering library/logic.
- **Logs** (`#panelLogs`): log rows mono `.n-technical`; severity as `.os-led` color, not full-row red.

## Related Code Files
- Modify: `static/panels.js` — render templates for skills/profiles/todos/insights/logs (confirm owners by grep).
- Modify: `static/index.html` — settings markup (rows + switches + 2×2 grid), other route static scaffolds (keep ids).
- Modify: `static/style.css` (V3 block) — settings rows/switches, secondary-route primitive application.

## Implementation Steps
1. **Settings**: convert appearance + behavior controls to row + right-aligned switch pattern; 2×2 font-size selector; thin red selection; verify no bottom-bar overlap (composer chips are chat-only, so settings should already be clear — confirm).
2. **Skills/Profiles/Todos**: apply `.os-row`/`.os-card`/`.os-led`; remove generic SaaS card styling; red only for active/critical.
3. **Insights**: wrap charts in `.os-surface`; relabel with type tiers; do not touch chart data/logic.
4. **Logs**: mono rows; severity LED; neutral default, red only for error severity.
5. Verify each route loads + interacts; settings persistence (`POST /api/settings`) unchanged.

## Success Criteria
- [ ] Settings: switches not checkbox cards; 2×2 font grid; thin red selection; no content overlap; persistence works.
- [ ] Skills/Profiles/Todos/Insights/Logs use shared primitives; consistent typography tiers.
- [ ] Red appears only for active/critical/error across all six routes.
- [ ] All routes load + function unchanged; `npm run lint:runtime` + `node --check` pass; console = 0 errors.

## Risk Assessment
- **Settings persistence coupling** → keep input ids/handlers wired to settings save; CSS/markup change only.
- **Insights chart library** → restyle container only; never touch chart init/data.
- **Scope creep across six routes** → apply primitives uniformly; resist per-route bespoke design (that's what phase 4 was for).
