---
title: "Hermes WebUI NothingOS V2 Design-System Brainstorm"
type: brainstorm-report
status: approved-design
created: 2026-06-27
modes:
  html: false
  wiki: false
source: ref/hermes-webui-nothingos-v2-redesign-brief.md
scope: full-responsive route-shell rewrite
---

# Hermes WebUI NothingOS V2 Design-System Brainstorm

## Summary

Sếp approved **Route-shell rewrite, full responsive**.

Core decision: V2 must rewrite shell + route surfaces. Not another CSS recolor.

Why: current app still behaves like old WebUI desktop shell squeezed into mobile. Bottom quick tray, rail/sidebar, split panels, and old route controls create the failures in the brief.

## Scout findings

- Project type: Python backend + vanilla JS/CSS static shell. No React, no Vite, no bundler.
- Primary UI files: `static/index.html`, `static/style.css`, `static/tokens.css`, `static/boot.js`, `static/os-widgets.js`, `static/workspace.js`.
- Current NothingOS layer: `static/tokens.css` + `static/os-widgets.js` + appended CSS in `static/style.css`.
- Global quick tray exists at `static/index.html` as `#osQuick`; rendered by `static/os-widgets.js` with Model / Workspace / Tools / etc.
- Current plan `plans/260627-0330-nothingos-webui-rewrite/plan.md` is completed but targeted V1 shell with ambient strip + OS rail + quick tray. New brief supersedes it.
- Repo currently has no `.claude/features/` directory found during scout; implementation must create/update feature docs because global workflow requires it.

## Problem-first inversion

### Solution-jumping diagnosis

The proposed solution says “redesign NothingOS fork.” Actual signal: users see a dark/red skin over old WebUI, not a true mobile-first OS command surface.

### Underlying problem

Hermes WebUI uses a desktop workbench shell as the dominant layout, so route workflows do not adapt to mobile, typography, state, and controls feel inherited rather than designed.

### Assumption challenges

| Assumption | Risk if wrong | Validation |
|---|---|---|
| Shell architecture is the root issue | If false, route CSS-only pass may be enough | Inspect mobile DOM: rail/sidebar/tray/split panes still occupy viewport |
| Vanilla JS can support route-shell rewrite | If false, rewrite becomes fragile | Keep IDs/API, move presentation only, run runtime lint + browser QA |
| Full responsive is needed now | If false, scope too large | Brief acceptance spans mobile plus Light/Dark full tokens and route behavior |
| Red overload is token + component issue | If false, route-specific CSS can fix | Audit chips, selected rows, cards, status pills |

### Problem statement

Users need Hermes WebUI to feel like a focused command surface. Mobile currently exposes desktop panels, global toolbar, generic cards, and overloaded red accents. This slows reading, hides content, clips panes, and undermines the NothingOS identity. Success means 390px routes are full-width, unclipped, readable, route-specific, and visually governed by dot/LED/status primitives.

### Alternative framings

1. **Mobile ergonomics problem** → prioritize shell breakpoints, no rail, no bottom overlay.
2. **Design-system consistency problem** → prioritize tokens, typography, red rules, component primitives.
3. **Route workflow problem** → prioritize per-route restructuring: Workspace, Chat, Jobs, Kanban, Memory, Settings.

Chosen framing: combine all three through **Route-shell rewrite**. Shell first, then route batches.

### Evidence status

Strong. Brief includes user critique + screenshot audit + concrete acceptance tests. Code scout confirms global tray, rail/sidebar, panel architecture still exist.

### Validation plan

- 390px viewport: no horizontal overflow.
- 390px viewport: no clipped side panel.
- Memory/Settings: no content hidden by fixed bottom bar.
- Code chips neutral by default.
- Chat selected row max two red cues.
- Kanban cards visible in first viewport; filters collapsed.
- Scheduled Jobs cards show schedule metadata.
- Light/Dark changes full page tokens.
- Browser console 0 page errors.
- Mobile visual QA screenshots for target routes.

### Stakeholder message

V2 should not patch colors again. The fastest credible path is a shell rewrite that preserves existing vanilla JS behavior while changing how routes own the viewport.

## Evaluated approaches

| Approach | Pros | Cons | Verdict |
|---|---|---|---|
| CSS containment pass | Fast, fewer JS/HTML changes | Repeats “skin over old WebUI”; likely misses clipped panes and route workflow | Reject for V2 |
| Primitive migration first | Cleanest long-term design system | Bigger upfront cost; risk over-engineering in vanilla monolith | Use selectively |
| Route-shell rewrite | Solves shell, route, toolbar, mobile root causes | Touches multiple files; needs staged QA | Recommended |

## Final recommended solution

Implement **Route-shell rewrite full responsive**.

### Responsive shell tiers

| Tier | Layout |
|---|---|
| Desktop ≥ 1024px | Compact rail + route content + optional context panel |
| Tablet 768–1023px | Compact launcher + full route content + optional drawer |
| Mobile < 768px | Top launcher + route title + full-width route surface + optional bottom sheet/dock |

Rules:

- No global bottom quick tray.
- No persistent rail below tablet width.
- No clipped split pane on mobile.
- Route header max 2 visible mobile actions.
- Red only active / critical / destructive / one primary CTA.
- Dot/display type only identity/status/short labels.
- Mono only technical metadata.

## Route decisions

### Workspace

- Mobile full-width file surface.
- Route dock only here: Search / New / Upload / More.
- Ambient strip: branch · delta · idle · model.
- Folder rows 48–56px touch targets.
- Breadcrumb/path chip.
- Hide/collapse chat/preview side panel on mobile.

### Chat

- Composer is the command surface; no global dock.
- Conversation list is full-page or drawer, not persistent rail.
- Remove fake close `X` on primary page.
- Normalize filter chips.
- Selected row max two red cues.

### Scheduled Jobs

- Header primary: `+ New Job`.
- Status LED: `● ACTIVE`, not green pill.
- Cards show next run, last run, cron/env/failures.
- Replace emoji with numeric index or monochrome glyph.
- Use empty space for timeline/activity diagnostics.

### Kanban

- Collapse advanced filters into bottom sheet.
- First viewport must show task cards.
- Mobile groups by status lanes.
- Move bulk action / preview dispatcher / tenant / assignee into sheet or overflow.
- Red only dispatcher or blocked state.

### Memory

- No bottom toolbar.
- Reader body uses UI sans, 18–22px mobile.
- Code chips neutral; red only alerts/search hits.
- Long paths wrap with `overflow-wrap:anywhere` and `box-decoration-break:clone`.
- Standalone `§` becomes dotted divider.
- Hierarchy: Memory module → MEMORY.md file → document heading.

### Settings

- No bottom toolbar.
- Appearance uses grouped rows + switches.
- Theme control changes full page tokens.
- Font size selector 2x2 or slider.
- Add Accent section or remove accent copy.
- Thin red selected outline only.

## Design-system primitives

- `RouteShell`: route-owned viewport shell.
- `RouteHeader`: title, status, max two mobile actions.
- `OsSegmentedControl`: balanced tabs/chips.
- `LedStatus`: idle/active/error/blocked dot/strip.
- `TactileButton`: mechanical press state.
- `BottomSheet`: mobile secondary controls.
- `RouteDock`: route-only dock for Workspace/Kanban.
- `TechMeta`: mono metadata.
- `DotDisplayLabel`: identity/status short labels.

Keep primitives light. No framework. No abstraction unless reused across routes.

## Implementation considerations

### Files likely touched

- `static/index.html` — route shell markup, panel placement, remove global tray usage.
- `static/style.css` — responsive shell, route surfaces, component primitives.
- `static/tokens.css` — V2 tokens/type aliases, red calibration, light/dark tokens.
- `static/os-widgets.js` — remove/re-scope quick tray; keep ambient/glance if useful.
- `static/boot.js` — route switching, theme picker, sidebar/drawer behavior.
- `static/workspace.js` — workspace panel/drawer behavior.
- `.claude/features/*.md` — create/update feature docs before/after implementation.

### Preserve

- Existing DOM IDs used by JS.
- Backend APIs.
- Vanilla JS no-build architecture.
- Existing auth/session/chat/workspace behavior.

### Avoid

- New React/Vite frontend.
- Copying Nothing logo/font/assets.
- Global red decoration.
- Generic CSS overrides that hide old architecture without fixing route ownership.

## Suggested implementation order

1. Feature docs + route inventory.
2. Shell + breakpoint architecture.
3. Remove/re-scope global quick tray.
4. Tokens + typography reset.
5. Workspace + Chat route migration.
6. Memory + Settings route migration.
7. Scheduled Jobs + Kanban route migration.
8. Interaction language pass: dot loader, LED, segmented progress, tactile states, bottom sheets.
9. QA: runtime lint, focused tests, browser screenshots, console check.

## Risks

| Risk | Mitigation |
|---|---|
| Breaking JS by moving markup | Preserve IDs, change wrappers/classes first |
| Scope creep into full app redesign | Only six target routes + shell + tokens |
| CSS cascade conflicts | Add V2 route/shell classes, retire old tray selectors gradually |
| Light mode partial application | Token-level flip, not preview-only tile |
| Mobile drawer regressions | Verify 390px each route after shell phase |

## Success metrics

- At 390px viewport: no horizontal overflow.
- At 390px viewport: no clipped side panel.
- Memory and Settings not obscured by fixed bottom bar.
- Code chips neutral by default.
- Chat selected row max two red cues.
- Kanban cards appear in first viewport after compact controls.
- Scheduled Jobs cards include next/last/cron-or-equivalent metadata.
- Light/Dark changes full page tokens.
- Browser console 0 page errors.
- Visual QA screenshots pass brief.

## Next steps

Recommended next command: `/ck:plan --tdd plans/reports/nothingos-v2-design-system-brainstorm-260627-2317-redesign-report.md`

Why TDD/default hybrid: this is a cross-route refactor with existing behavior to preserve. Plan should require checks per phase before broad styling.

## Unresolved questions

- None for brainstorm. Implementation planning must still verify available cron metadata from API before promising exact next/last run fields.
