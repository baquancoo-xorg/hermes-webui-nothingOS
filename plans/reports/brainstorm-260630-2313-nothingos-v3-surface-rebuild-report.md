# NothingOS V3 — Surface-Rebuild Redesign Brainstorm

> **Type:** brainstorm → design doc (handoff to `/ck:plan`)
> **Date:** 2026-06-30
> **Author:** ClaudeCode (brainstorm skill)
> **Decisions captured:** hybrid depth (advisor-decided), desktop+mobile parallel, all routes, brainstorm→plan
> **Inputs:** `ref/nothingos-webui-rewrite-spec.md`, `ref/nothingos-webui-reference.html`, `ref/hermes-webui-nothingos-v2-redesign-brief.md`, Image #1 (live desktop Chat), Explore architecture scout

---

## 0. TL;DR

Two prior rounds (`nothingos-webui-rewrite`, `nothingos-v2-design-system`) failed for one reason: **they recolored the old shell but never rebuilt the content inside each surface.** Right skeleton, wrong flesh.

The live app is NOT a recolored 1-column chat app — it is already a multi-column shell (`rail + sidebar + main + rightpanel`) that structurally matches the reference's OSRail + AgentSurface + GlanceWidgets. **So the bones are correct; the problem is the material filling them.**

**Chosen strategy — "Surface-internal structural rebuild, preserve the load-bearing skeleton":**
- KEEP the fragile JS-coupled shell (class names `.rail/.sidebar/.main/.rightpanel`, `switchPanel()`, `#panel*` ids, breakpoint logic) — ~50–65 JS call sites depend on it.
- REBUILD the low-coupling visual/DOM-content layer: design-system primitives, 3-tier typography, signal-only red, live ambient state, meaningful glance widgets, OS-style empty/list/card patterns, mobile single-surface behavior.

This is genuine structural change (new DOM content + interaction language per route), not a palette patch — but it avoids touching the navigation logic of a working complex app.

---

## 1. Problem statement

### What the user reported
Image #1 (live desktop Chat) still does not convey NothingOS spirit. It reads as "old WebUI + dark/red theme", confirming the V2 brief's own diagnosis (`hermes-webui-nothingos-v2-redesign-brief.md §0–1`).

### Concrete acceptance target (what "done" looks like)
The product stops feeling like `old WebUI + black theme + red accents` and starts feeling like `a focused OS command surface with NothingOS-inspired typography, dot/LED state language, and route-specific workflows` — on **both** desktop (per reference HTML) and mobile (per V2 brief, single-surface, no clipped panes, no horizontal overflow at 390px).

---

## 2. Codebase reality (scout findings — grounds every decision below)

| Fact | Evidence | Implication |
|---|---|---|
| Pure Python + vanilla JS, **no bundler** | `package.json` ("NOT a build step") | All edits go directly into `static/index.html`, `static/style.css`, `static/*.js`. No component framework, no JSX. |
| Shell is already multi-column | `style.css:278/311/830/1008` — `.layout`=flex → `.rail`(48px)+`.sidebar`(300px)+`.main`(flex)+`.rightpanel` | Reference 3-column layout is reachable by re-skinning surfaces, not by rebuilding the grid. |
| `switchPanel(name, opts)` centralized, data-attr driven | `panels.js:~10401` | 12 routes: chat, tasks, kanban, skills, memory, workspaces, profiles, todos, insights, logs, settings (+legacy plugin). Toggles `.panel-view.active` + `.main.showing-<name>` + `[data-panel]` nav. |
| ~50–65 JS call sites bind to shell class/id names | boot.js (~21), panels.js (~20–25), ui.js, workspace.js | Renaming the shell = high regression risk. **Preserve names.** |
| The "bottom toolbar MODEL/PROFILE/TOOLS" is NOT global | Composer chips inside `#composerBox .composer-footer` (`#composerModelChip`, `#profileChip`, etc.) | It only appears in Chat. The reference's "QuickCommandTray" is an idealization; the real equivalent is composer chips. Do not build a global bottom tray (V2 brief §2 also forbids it). |
| NothingOS V2 surfaces already exist but are thin | `index.html:171` `#osAmbient`; `index.html:1628` `#osQuick` (hidden/inert); `os-widgets.js:49` injects `.os-glance` into `.rightpanel` | Foundations are present. Ambient strip is a static text line; glance widget is near-empty. Make them alive, don't re-scaffold. |
| Tokens already mostly correct | `static/tokens.css` (loaded before style.css) | Color/typography token source matches spec §4. Gap is in *application*, plus missing LED + red-usage discipline. |

---

## 3. Evaluated approaches

### Approach A — Full structural shell rebuild (rejected)
Rebuild AppShell into new semantic components (OSRail/AgentSurface/QuickTray) with new class names, per spec §3.2 / §7 Phase 2.

- ✅ Cleanest naming; matches the "no cosmetic overlay" purity goal.
- ❌ Touches ~50–65 JS call sites (sidebar collapse, mobile overlay, panel switching) in a working app with cron/kanban/terminal/sessions. High regression cost.
- ❌ Low marginal payoff: the skeleton is *already* the right shape. We'd risk app stability to rename things users never see.
- **Verdict:** Over-engineered for the benefit. Violates KISS + surgical-change principle.

### Approach B — Continue recolor / token patch (rejected)
Add more CSS overrides on existing classes.

- ✅ Lowest risk, fastest.
- ❌ This is exactly what failed twice. Spec §8 names it the #1 anti-pattern. Will not produce OS feel.
- **Verdict:** Proven failure mode.

### Approach C — Surface-internal structural rebuild (CHOSEN)
Keep the load-bearing skeleton + routing; rebuild the content/visual/interaction layer inside each surface, route by route, on a shared primitive foundation.

- ✅ Genuine structural change (new empty-states, list-row anatomy, card anatomy, ambient behavior, mobile single-surface) — not recolor.
- ✅ Zero changes to fragile navigation logic → app stays stable.
- ✅ Phaseable + testable per layer; desktop and mobile per route in parallel.
- ⚠️ Retains legacy shell class names (naming impurity, invisible to users).
- **Verdict:** Best balance of OS-authenticity vs. stability. Selected.

---

## 4. Chosen design — detail

### 4.1 Foundation layer (build first; shared by all routes)

1. **Red discipline (signal, not paint).** Red allowed only for: selected nav state, the single primary CTA on a page, critical/blocked/error/destructive, active focus LED. Forbidden: every code chip, every card underline, multiple simultaneous cues. (V2 brief §2 P0, spec §2.1.) Add `--n-led-ok/warn/off` tokens (desaturated, not neon green).
2. **Typography 3-tier as utility classes.** `.n-display` (dot/display, geometric, uppercase, tracked — identity/labels/counters only) · base UI sans (nav, titles, body) · `.n-technical` (mono, tabular-nums — paths/branch/model/cron/timestamps only). Kill blanket mono/uppercase. (V2 brief §P0 typography.)
3. **OS primitives (CSS, reusable):**
   - `os-surface` (gradient + 1px border + inset highlight; depth from nesting, not drop shadow)
   - `os-dot-grid` (pseudo-element, opacity <.28, pointer-events none, no continuous animation)
   - **LED + segmented status strip** (idle/active/warn/blocked)
   - mechanical divider (dotted/§ → styled divider)
   - **OS list-row** (48–56px, touch-safe, dot label + LED + technical metadata)
   - **OS card anatomy** (`[dot label] [status LED] / title / metadata row / actions hidden until hover/expand`)
   - segmented control (equal zones, red selected underline only)
   - **bottom sheet** (mobile secondary controls)
   - dot-sweep loader / segmented progress (replace generic spinners)
4. **Ambient state, alive.** Wire `os-widgets.js` states (idle/thinking/tool_running/waiting_approval/error/complete) to real light language per spec §6 AmbientStatusStrip table. Hooks already exist (`setBusy`, `showApprovalCard`).
5. **Glance widgets, meaningful.** Populate `.os-glance` (run/turns/branch/model/approvals/cron) with real state already computed by the app.

### 4.2 Route tiers (all 12, ordered by effort/payoff)

- **Anchor — Chat:** OS empty-state (glanceable, not "What can I help with?" SaaS card), message surface treatment (user=raised right, assistant=less boxed, tool-call=collapsible mono module), composer as command-line with corner-marker focus (no glow). Composer chips normalized (signal red only on changed/active).
- **Content rebuild (brief's worst offenders) — Cron/Tasks, Kanban, Memory, Workspaces:**
  - Cron: LED status (`● ACTIVE`) not green pill, schedule metadata (next/last/cron/env), numeric/dot job glyph (no emoji), timeline in empty space. (Brief §4.3)
  - Kanban: compact filters → bottom sheet, cards in first viewport, status lanes on mobile, red only for dispatcher/blocked, fix 390px overflow. (Brief §4.4)
  - Memory: remove red-overload code chips (neutral default), readable body (18–22px mobile), `§` → dotted divider, long-path wrapping. (Brief §4.5)
  - Workspaces: full-width mobile, collapse chat panel, compact ambient strip, tactile 48–56px rows, breadcrumb chip, mobile chevrons. (Brief §4.1)
- **Apply-primitive (medium) — Settings, Skills, Profiles, Todos, Insights, Logs:** settings rows + right-aligned switches (no checkbox cards), 2×2 font-size grid, thin red selected outline; other routes adopt list-row/card primitives. (Brief §4.6)

### 4.3 Mobile single-surface (parallel with each route)
Use existing breakpoints (768/900/640) but change behavior: each route full-width, sidebar → drawer/bottom-nav (≤5 sections), no clipped side-pane, no horizontal overflow at 390px, touch targets ≥44px, filters in sheets. (V2 brief §2 P0, §6.)

---

## 5. Implementation considerations & risks

| Risk | Mitigation |
|---|---|
| Regression in nav/collapse/mobile-overlay | Do NOT rename shell classes/ids or touch `switchPanel`. Edit content + CSS only. Test all 12 routes + collapse + mobile overlay after each phase. |
| Red/mono creep returns | Encode discipline as utility classes + a QA checklist gate (brief §6); review per route. |
| Huge JS files (`ui.js` 751KB, `panels.js` 522KB) | Most route content is rendered by JS string templates — change templates, not logic. Locate render functions per route before editing. |
| Dot-grid / animation performance | Pseudo-elements only, opacity <.28, no full-grid continuous animation (spec §4.5). |
| Light mode parity | `tokens.css` already has `:root.light`; verify primitives read on both (THEMES contrast note). Single design language preserved. |
| No build step | Pure CSS/HTML/vanilla JS; `npm run lint:runtime` (ESLint runtime guard) is the only gate — run it + `node --check`. |

---

## 6. Success metrics / validation

- Desktop Chat reads as OS command surface (vs. reference HTML), not recolored chat.
- 390px mobile: 0 horizontal overflow, 0 clipped side-pane, content not obscured by any fixed bar.
- Red appears ≤1 primary block per page; code chips neutral by default; selected row ≤2 cues.
- Cron cards show schedule metadata; Kanban cards in first viewport; Memory body readable + neutral chips.
- Ambient strip animates per state; loaders are dot-sweep/segmented, not spinners.
- `npm run lint:runtime` passes; browser console = 0 page errors; both light/dark render cleanly.

---

## 7. Next steps & dependencies

1. Hand off to `/ck:plan` with this report as context.
2. Suggested phase order: Foundation primitives + tokens/type/red discipline → Ambient+Glance alive → Anchor (Chat) → Content rebuild (Cron/Kanban/Memory/Workspaces) → Apply-primitive routes → Mobile single-surface pass → QA gates (desktop 1440 + mobile 390 screenshots, lint, console).
3. `/ck:plan --tdd` is **not** the right fit (no unit-test harness for visual UI; the app is vanilla JS with only a runtime-lint guard). Use standard `/ck:plan` with per-phase visual QA acceptance.

## Unresolved questions
- None blocking. Open item for plan phase: confirm whether to ship a CSS-generated dot/display treatment for `.n-display` now, or defer the dot-matrix label effect to a later polish phase (cost vs. payoff to decide during planning).
