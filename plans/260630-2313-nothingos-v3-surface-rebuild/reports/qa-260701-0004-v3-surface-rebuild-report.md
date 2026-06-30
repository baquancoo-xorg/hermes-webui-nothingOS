# QA Report — NothingOS V3 Surface-Internal Rebuild

**Date:** 2026-07-01
**Mode:** /cook plan-path, run-through 1→7 (Validation S1 decision 2)
**App under test:** http://127.0.0.1:8787 (running, auth off, light+dark)

## Static gates — PASS

| Gate | Result |
|------|--------|
| `npm run lint:runtime` (eslint runtime guard, all static/*.js) | PASS, 0 findings |
| `node --check` on edited JS (os-widgets.js, panels.js, i18n.js) | PASS |
| CSS brace balance (style.css) | 3370/3370 balanced |
| Asset serve (index/style/tokens/os-widgets/i18n) | all 200 |
| Endpoint smoke (`/`, `/api/sessions`, `/api/settings`, `/api/workspaces`) | all 200 |
| App log | 0 errors |

## Files changed (scope-compliant)

- `static/tokens.css` — +`--n-led-ok/warn/off`, `--n-red-line` (dark + light parity).
- `static/style.css` — appended fenced V3 block (primitives + phase 3/4/5/6 route styles), all under `[data-skin="nothingos"]`.
- `static/os-widgets.js` — feed-only: ambient treatment unchanged-API; glance gains Approvals (binary state) + Cron (locale-safe `data-next`) widgets.
- `static/index.html` — empty-state eyebrow/display + suggestions as `.os-row`; kanban advanced filters wrapped in native `<details>` (ids/handlers preserved).
- `static/panels.js` — single surgical line: stamp `data-next` on `.cron-card-meta` for locale-safe glance read.
- `static/i18n.js` — +2 EN base keys (`empty_eyebrow`, `kanban_filters`); all locales fall back via `LOCALES.en[key]`.

## Hard-constraint adherence

- Shell ids/classes: **0 renamed/removed** (grep-verified osAmbient, emptyState, msgInner, composerBox, cron/kanban filter ids, logsOutput, mainInsights, fileTree, workspace tabs, all composer chip ids).
- `switchPanel()` / breakpoint structure (768/900/640): **untouched**.
- os-widgets.js: **feed-only** — 0 new API calls (reads `.approval-card.visible`, `#cronList .cron-card-meta[data-next]`, graceful `—`/`●` fallback).
- Red discipline: 1 sanctioned full-red block (dispatcher run button); active states use `--n-red-line` thin index/underline; chips neutral default / red-when-active.
- Single design language: all new color via `--os-*`/`--n-*` tokens (both `:root` dark + `:root.light` defined). No theme picker reintroduced.

## Code review (mandatory subagent) — DONE_WITH_CONCERNS, 0 blockers

Findings resolved:
1. Approvals glance = boolean → relabelled to signal glyph (`●`/`—`), not fake counter. **Fixed.**
2. Cron next-run was English-regex-coupled → now reads structured `data-next` (locale-safe). **Fixed (panels.js + os-widgets.js).**
3. Reviewer flagged 3 chip `.active` rules as dead → **false positive**: verified `composerWorkspaceChip`/`profileChip`/`composerToolsetsChip` all toggle `.active` (panels.js:5222/6012, ui.js:3639). Kept.
4. 2 untranslated i18n keys → added to EN base. **Fixed.**
5. `osRipple` mask-position inert → added center-out `mask-image` so the thinking ripple actually radiates. **Fixed.**

## Pending — manual visual QA (Sếp)

App is live at http://127.0.0.1:8787. Per session decision, Sếp performs the visual nghiệm thu. Suggested checklist (acceptance gate, phase 7):

- [ ] Desktop 1440: reads as OS command surface vs `ref/nothingos-webui-reference.html` (chat, cron, kanban, memory, workspaces, settings, skills, profiles, todos, insights, logs).
- [ ] Mobile 390: 0 horizontal overflow; no clipped side-pane; content not under a fixed bar (all 12 routes).
- [ ] Ambient strip: idle/thinking(ripple)/tool_running(segmented)/waiting_approval(red breathe)/error/complete each visibly distinct in a live session.
- [ ] Cron cards: LED status, schedule/next/last metadata, numeric glyph, no emoji/green pill.
- [ ] Kanban: advanced filters collapsed (`<details>`), cards in first viewport.
- [ ] Memory: neutral code chips, readable body (15px desktop / 17px mobile), dotted dividers, long-path wrap.
- [ ] Light + dark both clean (esp. Chat, Memory, Settings; LED + red-on-light contrast).
- [ ] Screenshots desktop 1440 + mobile 390 → this `reports/` dir.

## Unresolved questions

- None blocking. Screenshot capture deferred to Sếp's visual QA (no headless browser in this session).
