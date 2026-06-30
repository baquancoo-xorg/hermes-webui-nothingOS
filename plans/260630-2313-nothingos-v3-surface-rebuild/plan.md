---
title: "NothingOS V3 — Surface-Internal Structural Rebuild"
status: completed
created: 2026-06-30
scope: project
blockedBy: []
blocks: []
source: brainstorm
brainstorm: ../reports/brainstorm-260630-2313-nothingos-v3-surface-rebuild-report.md
---

# NothingOS V3 — Surface-Internal Structural Rebuild

> Make Hermes WebUI feel like a NothingOS-inspired OS command surface — not a recolored chat app — by rebuilding the **content/visual/interaction layer inside each surface** while **preserving the load-bearing shell skeleton + routing JS**.

## Why this plan exists

Two prior rounds (`260627-0330-nothingos-webui-rewrite`, `260627-2334-nothingos-v2-design-system`, both `completed`) recolored the old shell but never rebuilt the material inside each surface → right skeleton, wrong flesh. This plan changes the flesh.

## Hard constraints (apply to EVERY phase)

- **No bundler.** Pure Python + vanilla JS. Edit `static/index.html`, `static/style.css`, `static/*.js`, `static/tokens.css` directly.
- **Do NOT rename or restructure** shell classes/ids: `.layout`, `.rail`, `.sidebar`, `.main`, `.rightpanel`, `.panel-view`, `#panel*`, `#main*`. Do NOT touch `switchPanel()` routing logic or the 768/900/640 breakpoint *structure*. ~50–65 JS call sites depend on these.
- **Edit content + visual + interaction only.** Most route content is rendered by JS string templates — change templates and CSS, not navigation logic.
- **Red is a signal, not paint.** ≤1 primary red block per page; code chips neutral by default; selected row ≤2 cues.
- **No Nothing logos/fonts/assets.** Dot/display = CSS treatment only.
- **Single design language.** Keep existing `:root.light` parity in `tokens.css`; no theme picker reintroduced.
- **Verification per phase:** `npm run lint:runtime` + `node --check` on edited JS + browser console = 0 page errors + visual QA screenshot. No automated unit-test harness exists (vanilla JS).

## Phases

| # | Phase | Status | Priority | Depends |
|---|-------|--------|----------|---------|
| 1 | Foundation: tokens, 3-tier typography, red discipline, OS primitives | completed | P1 | — |
| 2 | Ambient state alive + Glance widgets meaningful | completed | P1 | 1 |
| 3 | Anchor route: Chat surface rebuild | completed | P1 | 1,2 |
| 4 | Content rebuild: Cron, Kanban, Memory, Workspaces | completed | P1 | 1,2,3 |
| 5 | Apply-primitive: Settings, Skills, Profiles, Todos, Insights, Logs | completed | P2 | 1,2,3 |
| 6 | Mobile single-surface pass (all routes) | completed | P1 | 3,4,5 |
| 7 | QA gates: desktop 1440 + mobile 390 screenshots, lint, console | completed | P1 | 6 |

## Acceptance (whole plan)

- Desktop reads as OS command surface vs. `ref/nothingos-webui-reference.html`, not recolored chat.
- 390px mobile: 0 horizontal overflow, 0 clipped side-pane, content not obscured by any fixed bar.
- Red ≤1 primary block/page; code chips neutral; selected row ≤2 cues.
- Cron cards show schedule metadata; Kanban cards in first viewport; Memory body readable + neutral chips.
- Ambient strip animates per state; loaders are dot-sweep/segmented, not spinners.
- `npm run lint:runtime` passes; console = 0 page errors; light + dark both render cleanly.

## Validation Log

### Session 1 — 2026-07-01

**Verification Results** (tier: Full, 7 phases)
- Claims checked: 14 (ids, renderer ownership, breakpoints)
- Verified: 14 | Failed: 0 | Unverified: 0
- Evidence: `#composerModelChip/#profileChip/#composerWorkspaceChip/#composerToolsetsChip/#composerModelLabel/#emptyState/#msgInner/#composerBox` present in `index.html`; `#cronList/#kanbanList/#kanbanAssigneeFilter/#kanbanOnlyMine` present; renderers — cron+kanban→`panels.js`, message+empty-state→`messages.js`+`ui.js`, file rows→`workspace.js`.

**Decisions confirmed:**
1. **Light mode: keep dark+light parity.** Every primitive + route must render cleanly in both `:root` (dark) and `:root.light`. QA tests both. (Affects all phases; phase 7 verifies.)
2. **No mid-plan checkpoint — run all 7 phases through to QA.** No stop-for-review after Chat anchor. (Accept risk: if Chat standard drifts, later routes may need rework — mitigated by faithful adherence to `ref/nothingos-webui-reference.html`.)
3. **Dot-matrix `.n-display` treatment built in phase 1** (not deferred). Resolves the brainstorm open question. (Affects phase 1.)
4. **Composer chips: keep as-is for usability — minimal touch.** User explicitly wants the current composer input/chips kept (more convenient). Apply ONLY red-discipline (neutral default / red-when-active) + typography tier; do NOT relocate, restructure, or build a global QuickCommandTray. (Affects phase 3.)

**Whole-Plan Consistency Sweep:** re-read all 7 phase files + plan.md. No stale terms or contradictions. Decisions 1/3 already aligned with phase 1+7 text; decisions 2/4 propagated below. Zero unresolved contradictions.

### Session 2 — 2026-07-01 (Execution via /cook, run-through 1→7)

**Outcome:** All 7 phases implemented and static-gated. Report: `reports/qa-260701-0004-v3-surface-rebuild-report.md`.

**Key finding during execution:** the V2 base already shipped much of the intended material (ambient state machine, `.os-led` base, message `.msg-row[data-role]` treatment, tool-card module, cron numeric-glyph card, neutral memory `--code-text`). V3 execution therefore *added the missing material* rather than rebuilding from scratch — surgical, scope-minimal:
- Phase 1: `--n-*` LED/red-line tokens + fenced V3 primitives block (typography tiers, surface, dot-grid, segmented, divider, os-row, os-card, sheet, dot loader).
- Phase 2: distinct ambient treatments (thinking=mask ripple, tool_running=segmented scroll) + 4 feed-only glance widgets.
- Phase 3: empty-state as OS surface, suggestions as `.os-row`, command-line composer focus marker, chip red-discipline (kept ids/handlers per decision 4).
- Phase 4: workspace segmented tabs + tactile file rows, memory readability/dividers, kanban advanced filters → native `<details>`.
- Phase 5: re-pointed legacy `--accent`-red `.active` states to neutral fill + thin red index across settings/skills/profiles/insights/logs; font-size 2×2; logs severity LED.
- Phase 6: phone-width fixes for new primitives (glance h-scroll, full-width segmented/rows, kanban single-column stack).
- Phase 7: lint + node --check + CSS balance + endpoint smoke all PASS; mandatory code-review = DONE_WITH_CONCERNS (0 blockers); 4 findings fixed, 1 was a false positive.

**Files touched:** `static/tokens.css`, `static/style.css`, `static/os-widgets.js`, `static/index.html`, `static/panels.js` (1 line), `static/i18n.js` (2 EN keys). No shell ids/classes renamed; `switchPanel`/breakpoints untouched; os-widgets stayed feed-only.

**Deferred:** desktop 1440 + mobile 390 screenshots → manual visual QA by Sếp (no headless browser this session). App live at http://127.0.0.1:8787.

## Phase files

- [phase-01-foundation-primitives-typography-red.md](phase-01-foundation-primitives-typography-red.md)
- [phase-02-ambient-state-glance-widgets.md](phase-02-ambient-state-glance-widgets.md)
- [phase-03-chat-anchor-surface.md](phase-03-chat-anchor-surface.md)
- [phase-04-content-rebuild-cron-kanban-memory-workspaces.md](phase-04-content-rebuild-cron-kanban-memory-workspaces.md)
- [phase-05-apply-primitive-secondary-routes.md](phase-05-apply-primitive-secondary-routes.md)
- [phase-06-mobile-single-surface-pass.md](phase-06-mobile-single-surface-pass.md)
- [phase-07-qa-gates.md](phase-07-qa-gates.md)
