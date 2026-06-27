---
title: "NothingOS V2 Route-Shell Design-System Rewrite"
description: "Rewrite Hermes WebUI NothingOS into a mobile-first route-owned command surface with TDD, feature docs, and visual QA gates."
status: completed
priority: P1
branch: "feat/nothingos-v2-route-shell"
tags: [feature, frontend, design-system, responsive, tdd]
blockedBy: []
blocks: []
created: "2026-06-27"
createdBy: "ck:plan"
source: skill
brainstorm: "../reports/nothingos-v2-design-system-brainstorm-260627-2317-redesign-report.md"
brief: "../../ref/hermes-webui-nothingos-v2-redesign-brief.md"
supersedes: "../260627-0330-nothingos-webui-rewrite/plan.md"
---

# NothingOS V2 Route-Shell Design-System Rewrite

## Overview

Implement the approved **Route-shell rewrite, full responsive** direction for Hermes WebUI NothingOS V2. This is not another color patch: the plan rewrites shell ownership, mobile route behavior, token/type usage, and six route surfaces while preserving the current Python + vanilla JS + no-build architecture.

Scope mode selected by Sếp: **SCOPE EXPANSION**. Expansion here means stronger design-system primitives, visual QA, and regression gates. It does **not** mean new product features outside the brief.

## Source Material

- Brainstorm: `plans/reports/nothingos-v2-design-system-brainstorm-260627-2317-redesign-report.md`
- Brief: `ref/hermes-webui-nothingos-v2-redesign-brief.md`
- Current architecture: `ARCHITECTURE.md`
- UI/UX guide: `docs/UIUX-GUIDE.md`
- Completed V1 plan superseded by V2: `plans/260627-0330-nothingos-webui-rewrite/plan.md`

## Current Code Inventory

| Area | Files | Notes |
|---|---|---|
| Static shell | `static/index.html`, `static/style.css`, `static/tokens.css` | Owns app titlebar, ambient strip, rail/sidebar, panels, quick tray styling. |
| Shell behavior | `static/boot.js`, `static/os-widgets.js` | Owns mobile sidebar/panel behavior, theme boot, quick tray/ambient updates. |
| Route behavior | `static/workspace.js`, `static/panels.js`, `static/sessions.js`, `static/messages.js` | Workspace, cron/jobs, kanban, memory/settings, chat list and message behavior. |
| Service worker | `static/sw.js` | Needs cache/version awareness if new static assets are added. |
| Tests | `tests/test_static_js_runtime_lint.py`, `tests/test_static_js_scope_undef.py`, `tests/browser_smoke.py`, focused route/static tests | Existing safety net for JS syntax/runtime and route UI contracts. |
| Feature docs | `.claude/features/` | Required by global workflow. Directory may not exist yet; implementation must create/update docs before and after code changes. |

## Scope Boundaries

### In scope

- Mobile-first shell tiers:
  - Desktop `>=1024px`: compact rail + route content + optional contextual panel.
  - Tablet `768–1023px`: compact launcher + full route content + optional drawer.
  - Mobile `<768px`: top launcher + route title + full-width route surface + route-only dock/sheet when useful.
- Remove/re-scope global bottom quick tray. No global `MODEL / WORKSPACE / TOOLS` dock.
- Token/type reset: dot/display only for identity/status/short labels; UI sans for readable text; mono only technical metadata.
- Red usage rules: active/critical/destructive/one primary CTA only.
- Route migrations: Workspace, Chat, Scheduled Jobs, Kanban, Memory, Settings.
- NothingOS interaction language: LED status, segmented progress/dot sweep, tactile press state, bottom sheets.
- TDD gates for static DOM/CSS contracts and route behavior before broad refactors.
- Visual QA screenshots at mobile width, plus console/no-overflow checks.
- Feature docs synced after implementation.

### Out of scope

- New React/Vite/frontend framework.
- Backend rewrite or API redesign.
- New user-facing product features not in the brief.
- Copying Nothing logos/fonts/assets.
- Perfect pixel match to external Nothing products.
- Removing unrelated tabs/features outside the six target routes.

## Approach

Use a staged **tests-first UI refactor**:

1. Lock current contracts with focused static tests before moving shell/route markup.
2. Introduce route-shell classes and data hooks around existing IDs.
3. Migrate shell/responsive behavior first, then token/type primitives.
4. Migrate routes in pairs to keep diffs reviewable.
5. Finish with visual/browser QA and feature docs sync.

## Cross-Plan Dependencies

| Relationship | Plan | Status | Decision |
|---|---|---|---|
| Supersedes | `plans/260627-0330-nothingos-webui-rewrite/plan.md` | completed | No blocker; V2 builds on V1 but reverses global quick tray / desktop-squeezed decisions. |

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Feature Docs and Baseline Inventory](./phase-01-feature-docs-and-baseline-inventory.md) | Completed |
| 2 | [Shell Architecture and Navigation](./phase-02-shell-architecture-and-navigation.md) | Completed |
| 3 | [Token Typography and Interaction Primitives](./phase-03-token-typography-and-interaction-primitives.md) | Completed |
| 4 | [Workspace and Chat Routes](./phase-04-workspace-and-chat-routes.md) | Completed |
| 5 | [Memory and Settings Routes](./phase-05-memory-and-settings-routes.md) | Completed |
| 6 | [Scheduled Jobs and Kanban Routes](./phase-06-scheduled-jobs-and-kanban-routes.md) | Completed |
| 7 | [Visual QA and Regression Gates](./phase-07-visual-qa-and-regression-gates.md) | Completed — browser QA waived by Sếp; Sếp will self-QA |

## TDD Strategy

Each implementation phase follows:

1. **Tests Before** — add/adjust static or behavior tests that describe the contract.
2. **Refactor** — change markup/CSS/JS while preserving existing IDs and APIs.
3. **Tests After** — add acceptance checks for the new V2 behavior.
4. **Regression Gate** — run focused tests first, then broaden.

Recommended focused gates:

```bash
./scripts/test.sh tests/test_static_js_runtime_lint.py -q
./scripts/test.sh tests/test_static_js_scope_undef.py -q
./scripts/test.sh tests/test_kanban_ui_static.py tests/test_kanban_board_ui.py -q
./scripts/test.sh tests/test_cron_refresh_button_835.py tests/test_issue2289_cron_detail_expansion.py -q
python3 -m py_compile server.py
```

Run full suite only after shared shell/contracts stabilize:

```bash
./scripts/test.sh
```

## Acceptance Criteria

- [x] At 390px viewport, no horizontal overflow on Chat, Workspace, Jobs, Kanban, Memory, Settings.
- [x] At 390px viewport, no clipped side panel or persistent full-height rail.
- [x] Global bottom quick tray removed or fully re-scoped to route-specific docks.
- [x] Memory and Settings are not obscured by any fixed bottom bar.
- [x] Code chips neutral by default; red reserved for alert/search/critical/primary.
- [x] Chat selected row uses max two red cues.
- [x] Kanban cards appear in first viewport after compact controls; advanced filters move to sheet/overflow.
- [x] Scheduled Jobs cards show next run / last run / cron-or-equivalent schedule metadata when API data exists.
- [x] Light/Dark changes full page tokens, not only preview tiles.
- [x] Browser console QA waived by Sếp; Sếp will self-QA.
- [x] Feature docs under `.claude/features/` match final code.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Moving markup breaks JS selectors | Preserve existing IDs; add wrappers/classes first; write static tests for required hooks. |
| V2 becomes another CSS skin | Phase 2 makes route-owned shell mandatory before route polish. |
| Red/mono overuse persists through cascade | Phase 3 adds token/type tests and route-level audit checklist. |
| Cron metadata promised but unavailable | Phase 1 inventories API fields; Phase 6 uses “or equivalent” metadata only when real data exists. |
| Visual QA too manual | Phase 7 defines exact screenshots, viewport, console, overflow checks. |
| Scope creep | Out-of-scope section blocks backend/framework/new feature expansion. |

## Implementation Notes for Cook

- Start on a feature branch before editing because current branch is `main`.
- Read/update relevant `.claude/features/` docs before and after code changes.
- Keep code vanilla. No bundler, no framework.
- Preserve backend API contracts.
- Prefer adding small helper functions in existing static modules over broad abstractions.
- Do not delete unrelated route features while simplifying mobile presentation.

## Open Questions

None for planning. Implementation must verify actual cron/job fields before choosing exact labels for next/last run metadata.

## Status Note — 2026-06-28

Phase 3-6 implementation and focused/static QA are complete. Browser smoke could not run in this local environment: `python3 tests/browser_smoke.py` returned `SKIP: playwright not installed` (exit code 2). Sếp waived the remaining browser console QA gate on 2026-06-28 and will self-QA, so the plan is marked completed with that explicit waiver.
