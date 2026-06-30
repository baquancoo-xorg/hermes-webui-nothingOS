---
phase: 1
title: "Foundation: tokens, 3-tier typography, red discipline, OS primitives"
status: completed
priority: P1
dependencies: []
---

# Phase 1: Foundation — tokens, typography, red discipline, OS primitives

## Overview
Build the shared CSS foundation every route reuses: finalize tokens, add a 3-tier typography system as utility classes, encode red-as-signal discipline, and ship reusable OS primitives (surface, dot-grid, LED/segmented status, mechanical divider, OS list-row, OS card anatomy, segmented control, bottom sheet, dot-sweep/segmented loaders). No route content changes yet — this is the toolbox.

## Requirements
- Functional: Primitives are class-based, theme-aware (dark + `:root.light`), and reusable without per-route CSS duplication.
- Non-functional: No new dependencies; pure CSS in `static/style.css` + `static/tokens.css`. Dot-grid uses pseudo-elements only, opacity <.28, `pointer-events:none`, no continuous full-grid animation (spec §4.5). Depth from borders/nesting, not drop shadow.

## Architecture
- `tokens.css` already holds color/spacing/radius/motion tokens (spec §4). Add only what's missing: `--n-led-ok` (#d8f8d8 desaturated), `--n-led-warn` (#f1d36b), `--n-led-off` (--os-faint), `--n-red-line` (rgba(255,59,48,.44)).
- Add a dedicated **primitives block** at the END of `static/style.css` (after legacy rules so cascade wins without `!important`), clearly fenced with a comment banner `/* ── NothingOS V3 primitives ── */`. Do NOT scatter edits through legacy selectors.
- Typography utilities: `.n-display` (display/dot, uppercase, letter-spacing .18em, weight 700+, identity/labels/counters ONLY), base UI sans is the default body, `.n-technical` (mono, `font-variant-numeric: tabular-nums`, paths/branch/model/cron/timestamps ONLY).

## Related Code Files
- Modify: `static/tokens.css` — add LED + red-line tokens.
- Modify: `static/style.css` — append V3 primitives block (typography utils, `.os-surface`, `.os-dot-grid`, `.os-led`, `.os-seg`, `.os-divider`, `.os-row`, `.os-card`, `.os-segmented`, `.os-sheet`, `.os-loader-dots`).
- Reference only (do not edit): `ref/nothingos-webui-reference.html` (visual contract for surface/dot/seg), `ref/nothingos-webui-rewrite-spec.md` §4–6.

## Implementation Steps
1. `tokens.css`: add `--n-led-ok/warn/off`, `--n-red-line` to `:root` and (where contrast differs) `:root.light`.
2. `style.css`: append fenced V3 block. Implement typography utilities first (`.n-display`, `.n-technical`).
3. Implement `.os-surface` (gradient + 1px `--os-line` + inset highlight), `.os-dot-grid` (radial-gradient pseudo-element, masked, low opacity).
4. Implement status language: `.os-led` (small dot, modifiers `--ok/--warn/--blocked/--off`, red breathing for blocked), `.os-seg` (segmented progress strip), `.os-divider` (dotted mechanical separator replacing raw `§`).
5. Implement layout primitives: `.os-row` (48–56px, touch-safe, `[dot label] [LED] / title / .n-technical metadata`), `.os-card` (card anatomy: dot label + LED top row, title, metadata row, actions revealed on hover/`[data-expanded]`), `.os-segmented` (equal zones, red selected underline only).
6. Implement `.os-sheet` (mobile bottom-sheet container: fixed bottom, translateY transition, safe-area padding) and `.os-loader-dots` (dot-sweep) / reuse existing `.os-seg` for segmented progress.
7. Add a throwaway `static/_v3-primitives-preview.html` (gitignored / deleted before merge) that renders each primitive in dark + light for visual QA, OR extend the existing reference file locally. Do not ship it.

## Success Criteria
- [ ] All primitives render correctly in BOTH dark and `:root.light`.
- [ ] `.n-display` / `.n-technical` exist and are NOT applied to body paragraphs anywhere yet.
- [ ] LED supports ok/warn/blocked(breathing)/off; no saturated green.
- [ ] Dot-grid: pseudo-element only, opacity <.28, no continuous animation.
- [ ] `npm run lint:runtime` passes; `node --check` clean on any touched JS (none expected this phase).
- [ ] Preview artifact NOT committed.

## Risk Assessment
- **Cascade conflicts with 5997-line legacy CSS** → append at end, fenced; prefer new class names over overriding legacy selectors; avoid `!important`.
- **Token collision** → new tokens use `--n-*` namespace distinct from legacy `--os-*`/`--accent`.
