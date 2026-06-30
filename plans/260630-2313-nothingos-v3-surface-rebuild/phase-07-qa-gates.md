---
phase: 7
title: "QA gates: screenshots, lint, console"
status: completed
priority: P1
dependencies: [6]
---

# Phase 7: QA gates

## Overview
Final verification against the brainstorm acceptance criteria and the V2 brief checklist (§6). Capture evidence (desktop 1440 + mobile 390 screenshots per route), run the runtime lint guard, confirm zero console errors, and verify red/typography discipline.

## Requirements
- Functional: all 12 routes work in both light + dark.
- Non-functional: documented evidence; no regression vs. pre-V3 behavior.

## Architecture
- No automated visual/unit test harness exists (vanilla JS, no bundler). QA is: runtime lint + `node --check` + manual browser capture + checklist review. Screenshots saved under this plan's `reports/`.

## Implementation Steps
1. Run `npm run lint:runtime`; run `node --check` on every edited `static/*.js`. Fix any failures.
2. Start the app (per repo `start.sh`/server.py); open each of the 12 routes.
3. Capture desktop 1440px screenshots (chat, cron, kanban, memory, workspaces, settings + the rest) → `reports/`.
4. Capture mobile 390px screenshots of the same routes → `reports/`.
5. Capture light + dark for at least Chat, Memory, Settings.
6. Verify each checklist item below; log defects + fix or file follow-up.

## Success Criteria (acceptance gate)
- [ ] Desktop reads as OS command surface vs. `ref/nothingos-webui-reference.html`, not recolored chat.
- [ ] 390px: 0 horizontal overflow; 0 clipped side-pane; content not obscured by fixed bar (all routes).
- [ ] Red: ≤1 primary red block/page; code chips neutral by default; selected row ≤2 cues.
- [ ] Typography: `.n-display` only for identity/labels/counters; mono only for technical metadata; body is readable sans.
- [ ] Ambient strip animates per state; loaders are dot-sweep/segmented, not generic spinners.
- [ ] Cron cards show schedule metadata; Kanban cards in first viewport; Memory body readable + neutral chips.
- [ ] `npm run lint:runtime` passes; `node --check` clean on all edited JS.
- [ ] Browser console = 0 page errors on every route.
- [ ] Light + dark both render cleanly; no theme picker present.
- [ ] No Nothing logo/font/asset committed; no secrets committed.
- [ ] Screenshots saved to `reports/` (desktop 1440 + mobile 390).

## Risk Assessment
- **Manual QA misses a route** → enumerate all 12 explicitly; check each.
- **Regression vs. upstream** → compare key flows (send message, run cron, open kanban card, edit memory, browse workspace, change settings) against pre-V3 behavior.
- **Light-mode contrast** → verify per THEMES.md contrast note, especially LED + red-on-light (`--os-red-deep`).
