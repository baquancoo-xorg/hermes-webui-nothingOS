---
phase: 2
title: "Ambient state alive + Glance widgets meaningful"
status: completed
priority: P1
dependencies: [1]
---

# Phase 2: Ambient state alive + Glance widgets meaningful

## Overview
Turn the two existing-but-thin NothingOS surfaces into living OS signals. The ambient strip (`#osAmbient`) currently shows a static text line; make it express agent state through light language per spec §6. The glance widgets (`.os-glance`, injected into `.rightpanel`) currently show near-empty placeholders; populate them with real state the app already computes.

## Requirements
- Functional: ambient strip visually distinguishes idle / thinking / tool_running / waiting_approval / error / complete; glance widgets show real run/turns/branch/model/approvals/cron data.
- Non-functional: feed-only — no new API calls, no stream-logic changes. Continue the observe-then-delegate wrapping pattern already in `os-widgets.js`.

## Architecture
- `static/os-widgets.js` already wraps `setBusy`, `showApprovalCard`/`hideApprovalCard`, `loadSession`, `renderMessages` and exposes `window.osAmbientState(state)`. State transitions are wired; only the **visual treatment** (CSS in phase 1 primitives) and the **glance data feed** need upgrading.
- Ambient visuals come from `[data-state]` on `#osAmbient` → CSS drives pulse/sweep/breathing using phase-1 `.os-seg` / `.os-led` motion tokens (spec §6 table: idle=dim line, thinking=dot ripple, tool_running=segmented strip, waiting_approval=red breathing, error=red pulse ×2, complete=white sweep then settle).
- Glance feed reads existing globals already used by `renderGlance()`: `S.messages`, `S.busy`, `#composerModelLabel`, `#gitBadge`. Extend to surface approvals + next cron run if cheaply available from existing DOM/state; otherwise show `—`, never invent data.

## Related Code Files
- Modify: `static/style.css` (V3 block) — ambient `[data-state]` visual states + glance widget styling using phase-1 primitives.
- Modify: `static/os-widgets.js` — enrich `renderGlance()` data sources (approvals count, cron next-run) reading existing state only; keep idempotent + cheap (existing 2s cadence).
- Modify (minimal): `static/index.html` line ~171 `#osAmbient` markup only if extra child nodes are needed for the sweep/ripple (keep `#osAmbient`, `#osAmbientLabel`, `#osAmbientPulse`, `#osAmbientState` ids intact).

## Implementation Steps
1. Define `#osAmbient[data-state="..."]` CSS for all 6 states using phase-1 motion primitives. `complete` self-settles to idle (timer already exists in `os-widgets.js`).
2. Verify state wiring end-to-end: trigger busy/approval/error in a live session and confirm `data-state` flips. Fix any missing hook (e.g. error path) without changing stream logic.
3. Restyle `.os-glance` widgets with `.os-card`/`.n-display`/`.n-technical` so the metric reads as an OS glance (run counter as `.n-display`, branch/model as `.n-technical`).
4. Extend `renderGlance()` to populate: current-run turns, busy/idle sub, model label, branch, + approvals-pending count and next cron (read from existing DOM/state; fall back to `—`).
5. Confirm glance still injects after `.rightpanel .panel-header` and does not break the resize handle / file browser.

## Success Criteria
- [ ] Ambient strip visibly differs across idle/thinking/tool_running/waiting_approval/error/complete in a live session.
- [ ] `complete` sweeps once then returns to idle.
- [ ] Glance widgets show real run/turns/branch/model; no fabricated values (missing → `—`).
- [ ] No new network calls added (feed-only preserved).
- [ ] `npm run lint:runtime` + `node --check static/os-widgets.js` pass; console = 0 errors.

## Risk Assessment
- **Overriding active approval/error when going busy** → preserve existing guard in `os-widgets.js` (`cur !== 'waiting_approval' && cur !== 'error'`).
- **Glance injection races with rightpanel render** → keep `ensureGlance()` idempotent; re-run on `loadSession`/`renderMessages` wraps already present.
- **Motion performance** → opacity/transform/background-position only (spec §4.6); no layout-loop animation.
