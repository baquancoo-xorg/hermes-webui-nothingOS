---
phase: 3
title: "Anchor route: Chat surface rebuild"
status: completed
priority: P1
dependencies: [1, 2]
---

# Phase 3: Anchor route — Chat surface rebuild

## Overview
Rebuild the Chat route (the main surface in Image #1) into the reference-quality OS command surface. This route sets the visual/interaction standard every later route copies. Targets: OS empty-state (replace generic "What can I help with?" SaaS card), message treatment, collapsible tool-call modules, command-line composer, normalized composer chips.

## Requirements
- Functional: empty-state, message stream, tool-call rendering, and composer all use phase-1 primitives; chat send/stream behavior unchanged.
- Non-functional: keep `#mainChat`, `#messages`, `#msgInner`, `#emptyState`, `#composerWrap`, `#composerBox`, `textarea#msg` ids and the composer chip ids (`#composerModelChip`, `#profileChip`, `#composerWorkspaceChip`, `#composerToolsetsChip`) — restyle and re-template content only.

## Architecture
- Empty-state (`#emptyState`, index.html ~line 446 + suggestion buttons ~458) → glanceable OS surface: dot-matrix mark, `.n-display` short prompt, 3 suggestion rows as `.os-row`, not generic cards.
- Message treatment: user = raised right panel (`.os-surface` raised), assistant = less-boxed left content block, tool-call = collapsible `.os-card`/technical module with `.n-technical` mono header + `.os-seg` progress. Find the message render function (likely in `static/messages.js` — 321KB — and `static/ui.js`); change template strings only.
- Composer: command-line feel; focus state = white border + small red corner marker (NOT glow); no dot texture behind input.
- **Composer chips — minimal touch (Validation S1 decision 4):** user wants the current composer input/chips kept as-is for usability. Do NOT relocate, restructure, or build a global QuickCommandTray. Apply ONLY: neutral-default / red-when-active discipline + typography tier. Keep all chip ids + click handlers untouched.

## Related Code Files
- Modify: `static/index.html` — `#emptyState` + suggestion markup (~446–461), composer footer chip markup if needed (keep ids).
- Modify: `static/style.css` (V3 block) — chat empty-state, message bubbles, tool-call module, composer focus/chips.
- Modify: `static/messages.js` and/or `static/ui.js` — message/tool-call render templates (locate render fn first; change HTML strings, not logic).
- Reference: `ref/nothingos-webui-reference.html` (AgentSurface + composer), spec §6 AgentSurface/Composer.

## Implementation Steps
1. Locate the render functions for: empty-state, a user message, an assistant message, a tool-call block. Grep `messages.js`/`ui.js` for `emptyState`, `msgInner`, tool-call class names. Map before editing.
2. Rebuild `#emptyState` markup + CSS as OS surface (dot mark + `.n-display` line + `.os-row` suggestions). Preserve suggestion click handlers.
3. Restyle user vs assistant messages per spec §6 (user raised-right, assistant less-boxed). Template-string changes only.
4. Convert tool-call rendering to a collapsible `.os-card` technical module: mono header (tool name), `.os-seg` while running, collapsed-by-default detail.
5. Restyle composer: command-line input, corner-marker focus, no glow, no dot texture behind text. Chips: ONLY apply neutral-default / red-when-active + typography tier — keep layout, ids, handlers as-is (Validation S1 decision 4). <!-- Updated: Validation Session 1 - keep composer chips as-is, minimal touch -->
6. Optional dot-matrix `.n-display` on the empty-state mark is already available from phase 1 (built there per Validation S1 decision 3).
6. Verify: send a message, run a tool, trigger approval — stream, scroll, and ambient strip (phase 2) all behave. No regression in `setBusy`/scroll anchors (`assistant_turn_anchors.js`).

## Success Criteria
- [ ] Empty-state reads as OS surface, not a generic SaaS card; suggestions still work.
- [ ] User/assistant/tool-call messages visually distinct per spec; tool-call collapses.
- [ ] Composer focus = corner marker, no glow; chips neutral unless active.
- [ ] Send + stream + scroll-anchor + ambient state unchanged functionally.
- [ ] `npm run lint:runtime` + `node --check` on edited JS pass; console = 0 errors.
- [ ] Desktop screenshot approximates `ref/nothingos-webui-reference.html` AgentSurface.

## Risk Assessment
- **Huge JS files (messages.js 321KB, ui.js 751KB)** → locate exact render fn first; edit template strings surgically; do not refactor surrounding logic.
- **Scroll-anchor coupling** (`assistant_turn_anchors.js`) → do not change message DOM ids/structure that anchoring relies on; restyle via classes.
- **Streaming render** → changing template must preserve incremental-append behavior; test mid-stream.
