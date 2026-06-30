---
phase: 6
title: "Mobile single-surface pass (all routes)"
status: completed
priority: P1
dependencies: [3, 4, 5]
---

# Phase 6: Mobile single-surface pass

## Overview
Make every route a full-width single-surface mobile experience per V2 brief §2/§6. Use the EXISTING breakpoints (768/900/640) — change behavior, not the breakpoint structure JS depends on. No clipped side-panes, no persistent rail below tablet, no horizontal overflow at 390px.

## Requirements
- Functional: at <768px each route is full-width; sidebar opens as intentional drawer; rightpanel is slide-over not a squeezed column; filters open as sheets.
- Non-functional: touch targets ≥44px; no horizontal overflow at 390px; content never obscured by a fixed bar (safe-area padding where a dock exists).

## Architecture
- The shell already collapses: rail hidden <768px, sidebar→fixed overlay, rightpanel→slide-over (scout: style.css @media 768/900/640). This phase ensures each route's NEW content (phases 3–5) behaves correctly inside that collapse, and fixes residual desktop-squeeze.
- Navigation: keep existing hamburger/drawer; ensure ≤5 primary sections reachable; route title not truncated.
- Route-specific docks only where the brief allows (Workspace dock; Kanban conditional). Chat = composer only, no global bottom bar. Memory/Settings = no dock.

## Related Code Files
- Modify: `static/style.css` — mobile rules within existing `@media (max-width:768px|900px|640px)` blocks for the new V3 primitives + per-route content.
- Modify (minimal): `static/index.html` — any mobile-only dock/sheet trigger markup (keep shell ids).
- Verify: `static/boot.js` mobile overlay toggles still work (do NOT change their selectors).

## Implementation Steps
1. Audit each of the 12 routes at 390px: list overflow / clipped-pane / obscured-content defects.
2. Fix Chat: full-width stream, composer safe-area bottom padding, chips wrap without overflow.
3. Fix Workspace/Memory: no clipped chat panel behind; reader/browser full-width; Workspace route dock with safe-area.
4. Fix Kanban: filters in `.os-sheet`; cards in first viewport; no new-task-row overflow.
5. Fix Cron/Settings/secondary routes: full-width rows; no fixed-bar overlap.
6. Confirm drawer + slide-over open/close via existing `boot.js` logic (unchanged selectors).
7. Re-test at 390px and 768px (tablet) for layout integrity.

## Success Criteria
- [ ] 390px: 0 horizontal overflow on all 12 routes.
- [ ] 390px: no clipped side-pane; no persistent full-height rail.
- [ ] Route titles not truncated; ≤2 visible header actions on mobile.
- [ ] Memory + Settings content not obscured by any fixed bar.
- [ ] Touch targets ≥44px; filters collapse into sheets.
- [ ] Sidebar drawer + rightpanel slide-over still toggle correctly (boot.js unchanged).
- [ ] `npm run lint:runtime` passes; console = 0 errors.

## Risk Assessment
- **Breaking existing mobile overlay JS** → do not change `.sidebar`/`.rightpanel`/`.layout` selectors or boot.js toggle logic; only adjust CSS within existing media blocks + add sheet markup.
- **Safe-area insets** → use `env(safe-area-inset-bottom)` for any fixed dock.
- **Tablet (768–900px) middle state** → verify the in-between tier doesn't regress while fixing phone width.
