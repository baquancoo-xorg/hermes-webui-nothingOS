# Hermes WebUI NothingOS V2 Redesign Brief

> **Purpose:** Correct the current Hermes WebUI NothingOS fork from “dark recolor/theme skin” into a real NothingOS-inspired product experience.  
> **Audience:** Dominium + ClaudeCode implementation pass.  
> **Date:** 2026-06-27  
> **Primary evidence:** Dominium field feedback + six mobile screenshots from installed WebUI.  
> **Provenance:** User critique 🟢 `#own-thought`; screenshot visual audit 🔵 `#external-verified`; synthesis 🟡 `#ai-summary-verified`.

---

## 0. TL;DR

The current implementation is not a true NothingOS-inspired redesign. It is mostly a **black/red skin over the old WebUI layout**.

| Problem | Current symptom | V2 requirement |
|---|---|---|
| Bottom toolbar | `MODEL / WORKSPACE / TOOLS` fixed bar is bulky, redundant, clips content, and appears on pages where it is not contextual. | Remove it from most pages. Replace with route-specific command dock only when useful. |
| Mobile layout | Desktop split panes / side rail are squeezed into iPhone viewport. | Mobile must be single-surface, full-width, route-specific. No clipped side panels. |
| Typography | Mono/uppercase is overused; text style feels generic or hacked. | Use a 3-tier NothingOS type system: dot/display for identity, geometric sans for UI, mono only for technical metadata. |
| Primary color | Red is used as decoration/theme and sometimes too bright/generic. | Red is a calibrated signal color: active, critical, destructive, or one primary action. |
| Page design | Chat, Jobs, Kanban, Memory, Settings still use old form/card patterns. | Rebuild core primitives and each route pattern, not just CSS colors. |
| NothingOS language | Dotted mark appears, but rest of UI lacks glyph/LED/dot/system rhythm. | Add dot-grid, segmented LED status, mechanical dividers, and OS-like control surfaces. |
| Old WebUI residue | Close buttons, desktop toolbar icons, generic chips/cards, old side panels remain. | Remove desktop/window metaphors from mobile and convert to mobile-first OS patterns. |

---

## 1. Root cause

The previous pass changed visual tokens and appended CSS to prebuilt assets. That can produce a surface-level dark/red theme, but cannot produce a true design-system rewrite because:

1. The old layout architecture remains intact.
2. The same components still decide hierarchy, spacing, and mobile behavior.
3. The bottom/status toolbar remains global instead of contextual.
4. Route-level UX remains desktop-admin style.
5. Typography and interaction states are not rebuilt.

V2 must therefore be a **component + route architecture rewrite**, not another palette patch.

---

## 2. Non-negotiable V2 principles

### P0 — Mobile-first, not desktop squeezed

Below tablet width:

```txt
- No persistent left rail consuming screen width.
- No partially visible side panel.
- No clipped split panes.
- No always-visible desktop toolbar with 5–7 icons.
- Each route must be a full-width mobile surface.
```

Allowed mobile navigation patterns:

- compact top launcher/menu,
- bottom nav/dock with 4–5 sections max,
- drawer opened intentionally,
- route-specific bottom command dock.

### P0 — Remove global bottom toolbar

The fixed bottom toolbar (`MODEL / WORKSPACE / TOOLS`) is not allowed globally.

| Current issue | Required fix |
|---|---|
| Covers content in Memory/Settings | Add no overlay unless route requires it; if fixed, add safe-area bottom padding. |
| Duplicates state already in route | Move state into route header/ambient strip. |
| Takes too much vertical space | Use compact status strip or bottom dock only on command-heavy pages. |
| All cards use red underline | Red underline only for active/changed/critical state. |

Suggested replacements:

- Chat page: no bottom status toolbar; use composer only.
- Workspace page: route-specific dock `Search / New / Upload / More`.
- Memory page: no dock; use reader/editor toolbar that hides while reading.
- Settings page: no dock.
- Kanban page: sticky action dock only if dispatch/run is the main task.

### P0 — Red is signal, not theme paint

Use red only for:

- selected navigation state,
- one primary CTA on a page,
- critical/blocked/error/destructive state,
- active focus LED/dot.

Do not use red for:

- every code chip,
- every bottom toolbar card,
- every selected text + icon + bar simultaneously,
- generic status labels like normal active jobs.

Recommended tokens:

```css
--nothing-red: #ff3b30;
--nothing-red-deep: #2a0706;
--nothing-red-soft: rgba(255, 59, 48, .12);
--nothing-red-line: rgba(255, 59, 48, .44);
```

### P0 — Typography must become a system

Current state: mono/uppercase everywhere or generic sans elsewhere. V2 needs a deliberate type ladder.

| Tier | Font/style | Use |
|---|---|---|
| Display/dot | CSS dot-matrix treatment or custom generated pattern, not proprietary Nothing font | App logo, short route labels, status counters, loaders. |
| UI sans | Geist / Satoshi / Space Grotesk style geometric sans | Navigation, titles, controls, cards, settings labels. |
| Technical mono | JetBrains Mono / Geist Mono | Paths, branch names, file metadata, model names, cron expressions, timestamps. |

Rules:

- Dot/display style is an accent, not body copy.
- Mono is for technical metadata only.
- Large note body text should be readable sans, not huge mono-like paragraphs.
- Section labels can be uppercase/tracked, but long labels cannot.

### P0 — NothingOS is an interaction language

Add system behaviors:

- segmented LED-like progress strip,
- dot sweep loader,
- red breathing dot for blocked/error,
- white/gray LED for idle/active,
- tactile press state,
- route transitions that feel like OS panes, not web modals,
- bottom sheets for secondary controls on mobile.

---

## 3. Global component replacements

### 3.1 App shell

Replace the current mobile shell with responsive shell tiers:

```txt
Desktop ≥ 1024px:
  OS rail + route header + main content + optional contextual side panel.

Tablet 768–1023px:
  compact OS rail + full content + optional drawer.

Mobile < 768px:
  no persistent rail; top launcher + route title + full-width content + optional bottom nav/dock.
```

### 3.2 Route header

Current: hamburger + brand + truncated title + too many icons + X.

V2:

```txt
[brand mark] [route title]                         [primary action] [more]
[ambient status strip: branch · run · sync · model]   optional, compact
```

Rules:

- Max 2 visible actions on mobile.
- Remove `X` from primary pages unless it is a real modal/drawer close.
- No truncated brand/title in header. Use brand mark + clear route label.

### 3.3 Bottom command dock

Only route-specific.

Examples:

| Route | Dock? | Contents |
|---|---|---|
| Workspace | yes | Search, New, Upload, More |
| Kanban | conditional | Run Dispatcher / Add Task / Filter |
| Chat | no global dock | composer only |
| Memory | no persistent dock | reader toolbar hides/collapses |
| Settings | no | none |
| Scheduled Jobs | no persistent dock | New Job primary in header/card |

### 3.4 Segmented control

Replace one-pill-plus-floating-label patterns.

Example:

```txt
[ Files  ] [ Artifacts 0 ]
```

Rules:

- equal zones,
- red only as selected underline/dot,
- no unbalanced pill + plain text pair.

### 3.5 Card/surface language

Current: generic dark rounded rectangles.

V2 cards:

- fewer full cards,
- more line-based grouping,
- subtle dot/corner markers,
- mechanical separators,
- lower/varied radius,
- no generic glow.

Card anatomy:

```txt
[dot label]                         [status LED]
primary content / title
technical metadata row
contextual actions hidden until hover/long-press/expanded
```

---

## 4. Page-specific requirements

## 4.1 Workspace / Files page

### Current failures observed

- Old chat/WebUI panel remains partially visible.
- Main workspace is clipped by split-pane layout.
- Header has too many generic icons.
- Branch/status cards push file list too low.
- `Files` vs `Artifacts` tab is unbalanced.
- Disclosure triangles feel desktop-tree, not mobile-first.

### V2 target

Mobile structure:

```txt
Top bar:
  [H mark] Workspace                    [New] [More]
Ambient strip:
  master · 1Δ · idle · gpt-5.5
Segment:
  Files / Artifacts
Path/search:
  /CoWorkOS-Command-Center              [Search]
List:
  full-width touch rows, 48–56px each
Bottom dock:
  Search / New / Upload / More          only on workspace route
```

Requirements:

- Full-width on mobile.
- Hide/collapse chat panel.
- Compress `CURRENT RUN` and `MEMORY MODE` into one compact ambient strip.
- Make folder rows tactile and touch-safe.
- Use path/breadcrumb chip.
- Replace tiny disclosure triangles with mobile chevrons or open-row behavior.

---

## 4.2 Chat / Conversation list

### Current failures observed

- Persistent left nav rail consumes mobile width.
- Header has desktop-like `X` close.
- Filters use inconsistent styles and a blue dot.
- Selected conversation uses too many red cues: title + icon + bar + border.
- Search/chips feel generic SaaS.

### V2 target

```txt
Top:
  Chats                                [+]
Search:
  compact technical search field
Filter row:
  All / Unassigned / Cron Jobs / More  normalized chip system
List:
  grouped by Today / Yesterday / Week
Selected:
  one cue only: red left LED OR red icon, not all at once
```

Requirements:

- Remove mobile left rail or convert to bottom nav/drawer.
- Remove `X` on full-page chat history.
- Use only black/white/gray/red; remove blue dot unless semantic and documented.
- Conversation titles should be off-white; red only as structural selected marker.
- Section headers can use dot/mono label style.

---

## 4.3 Scheduled Jobs

### Current failures observed

- Generic rounded job cards.
- Robot emoji breaks the design system.
- Green `active` pill is generic.
- Cards lack schedule metadata.
- Empty black area looks unfinished.
- `+` primary action is too weak.

### V2 target

```txt
Header:
  Scheduled Jobs                       [+ New Job]
Status:
  02 active · last sync 21:32
Timeline:
  now marker + next runs
Cards:
  01 Weekly-Looping-Learning
  next 08:00 · cron 0 8 * * 1 · last ok · env default
  [Run now] [Pause] [Logs]
```

Requirements:

- Replace emoji with custom monochrome/dot job glyph or numeric index.
- Status as LED: `● ACTIVE`, not large green pill.
- Show next run, last run, cron/environment, failures.
- Use empty space for schedule timeline or activity diagnostics.
- Make `+ New Job` visible primary action.

---

## 4.4 Kanban

### Current failures observed

- Filter stack consumes half the screen before tasks.
- Left nav rail cramps content.
- Buttons/inputs risk horizontal overflow.
- Looks like generic admin controls.
- `RUN DISPATCHER` is prominent but visually generic.
- Mobile view is task list, not clear Kanban lanes.

### V2 target

Mobile hierarchy:

```txt
Header: Kanban                         [+] [More]
Search
Filter summary: All assignees · All tenants · Mine off  [Tune]
Primary: RUN DISPATCHER                only if relevant
Status lanes:
  BLOCKED 1
    task card
  DONE 6
    task card
```

Requirements:

- Collapse advanced filters into a bottom sheet.
- Show cards earlier in viewport.
- Group cards by status lanes on mobile.
- Convert `Bulk action`, `Preview dispatcher`, tenant/assignee filters into overflow/filter sheet.
- Fix horizontal overflow in new task row.
- Use red only for dispatcher or blocked, not generic UI decoration.

---

## 4.5 Memory / Notes

### Current failures observed

- Bottom toolbar clips content and overflows horizontally.
- Inline code chips use red everywhere, causing red overload.
- Body text too large for dense notes.
- Long paths/URLs wrap awkwardly.
- Header actions are generic.
- `MEMORY`, `My Notes`, `MEMORY.md` hierarchy is unclear.

### V2 target

```txt
Header:
  Memory                               [+] [Sync state]
File header:
  MEMORY.md · edited 03:46
Reader:
  readable body text, 18–22px mobile
  code chips neutral; red only for alerts/search hits
Section breaks:
  dotted divider instead of raw §
No global bottom toolbar.
```

Requirements:

- Remove bottom toolbar from reader.
- Add bottom padding if any fixed toolbar exists.
- Code chips default off-white/gray, not red.
- Allow long code/path wrapping with `overflow-wrap:anywhere` and `box-decoration-break:clone`.
- Render standalone `§` as styled dotted divider.
- Clarify hierarchy: module = Memory, file = MEMORY.md, heading = document heading.

---

## 4.6 Settings / Appearance

### Current failures observed

- Theme picker is nested card-heavy and generic.
- Light preview is only a swatch, not evidence of full light mode.
- Font size grid is imbalanced: 3 + 1 layout.
- Old checkbox controls remain.
- Bottom toolbar overlaps settings.
- Appearance contains workspace behavior settings.
- Subtitle mentions accent colors but no accent color control visible.

### V2 target

```txt
Appearance
Theme           [Dark] [Light]              real preview tiles
Typography      2x2 size grid or slider
Accent          Nothing Red / Mono / System  if configurable
Interface       density / motion / contrast
Workspace behavior goes to Workspace settings, not Appearance.
```

Requirements:

- Replace checkbox cards with grouped settings rows + right-aligned switches.
- Use 2x2 font-size selector.
- Remove bottom toolbar from Settings.
- Implement true light/dark mode page tokens if theme switch exists.
- Add accent section or remove `accent colors` from copy.
- Red selected outline should be thin; avoid nested red rectangles.

---

## 5. Visual token reset

### 5.1 Color

```css
:root,
[data-skin="nothingos-v2"] {
  --n-bg: #070706;
  --n-bg-elevated: #0d0d0b;
  --n-surface: #12120f;
  --n-surface-2: #191914;
  --n-line: rgba(245, 242, 232, .10);
  --n-line-strong: rgba(245, 242, 232, .18);

  --n-text: #f5f2e8;
  --n-text-muted: #aaa79d;
  --n-text-faint: #6f6c63;

  --n-red: #ff3b30;
  --n-red-soft: rgba(255, 59, 48, .12);
  --n-red-line: rgba(255, 59, 48, .44);

  --n-led-ok: #d8f8d8;       /* not saturated green */
  --n-led-warn: #f1d36b;
  --n-led-off: #6f6c63;
}
```

### 5.2 Typography

```css
:root {
  --font-ui: "Geist", "Satoshi", system-ui, sans-serif;
  --font-display: "Space Grotesk", "Geist", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", "Geist Mono", ui-monospace, monospace;
}

.n-display-label {
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: .18em;
  font-weight: 750;
}

.n-technical {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}
```

Dot-matrix should be CSS treatment for short marks, not proprietary Nothing font.

### 5.3 Radius

```css
--r-chip: 8px;
--r-control: 12px;
--r-card: 18px;
--r-major: 24px;
```

Avoid using huge rounded rectangles on every element.

---

## 6. Component acceptance checklist

### Shell

- [ ] Mobile has no clipped side pane.
- [ ] Mobile has no persistent full-height nav rail unless viewport is tablet/wide.
- [ ] Route title is never truncated in normal mobile width.
- [ ] Header has max two visible actions on mobile.
- [ ] `X` appears only for actual dismissible panels.

### Bottom toolbar

- [ ] Global `MODEL / WORKSPACE / TOOLS` toolbar removed.
- [ ] No fixed toolbar covers content.
- [ ] Any route-specific dock uses safe-area padding.
- [ ] No toolbar item is clipped horizontally.

### Typography

- [ ] Dot/display treatment used only for identity/status/short labels.
- [ ] Body text uses readable UI sans.
- [ ] Mono used only for technical metadata.
- [ ] Long labels are not letter-spaced excessively.

### Red usage

- [ ] Red used for active/critical/primary only.
- [ ] No page has more than one primary red block.
- [ ] Code chips are neutral by default.
- [ ] Selected row uses max two cues.

### Mobile ergonomics

- [ ] Touch targets ≥ 44px.
- [ ] Filters collapse into sheets on mobile.
- [ ] Advanced actions are not all visible at once.
- [ ] No horizontal overflow at 390px width.

### NothingOS identity

- [ ] Dot/LED/glyph state language appears beyond logo.
- [ ] Loaders are dot sweep or segmented strip, not generic spinners.
- [ ] Status is shown as LED/dot/strip language.
- [ ] Cards feel like OS modules, not generic SaaS cards.

---

## 7. ClaudeCode implementation prompt

```txt
You are redesigning the Hermes WebUI NothingOS fork. The current app is only a dark/red skin over the old WebUI. Your task is a V2 design-system rewrite, not another CSS recolor.

Read:
- docs/hermes-webui-nothingos-v2-redesign-brief.md
- existing frontend/static assets and actual served bundle.

Core goals:
1. Remove global bottom toolbar MODEL / WORKSPACE / TOOLS from routes where it is redundant.
2. Implement mobile-first shell: no clipped split panes, no persistent side rail below tablet width.
3. Rebuild typography system: dot/display for identity, UI sans for body/control text, mono only for technical metadata.
4. Calibrate Nothing red and use it only for active/critical/primary states.
5. Redesign Workspace, Chat, Scheduled Jobs, Kanban, Memory, and Settings pages according to the page-specific requirements in the brief.
6. Add true NothingOS interaction language: dot loaders, LED status, segmented progress, tactile press states, bottom sheets for secondary controls.
7. Do not copy Nothing logo/font/assets. Make it NothingOS-inspired, not trademark clone.

Acceptance tests:
- At 390px viewport, no horizontal overflow.
- At 390px viewport, no clipped side panel.
- Memory and Settings content are not obscured by any fixed bottom bar.
- Code chips are not red by default.
- Chat selected row uses max two red cues.
- Kanban cards appear in the first viewport after compact controls; advanced filters are collapsed.
- Scheduled Jobs cards show next run / last run / cron or equivalent schedule metadata.
- Light/Dark setting, if present, changes the full page tokens, not just a preview tile.
- Browser console has 0 page errors.
- Visual QA screenshots for mobile routes pass against this brief.
```

---

## 8. Suggested implementation order

1. **Shell + mobile breakpoints** — fix architecture before polishing.
2. **Remove/rebuild bottom toolbar** — unblock Memory/Settings readability.
3. **Token/type reset** — stop red/mono overuse.
4. **Workspace + Chat mobile pages** — most visible UX failures.
5. **Memory + Settings** — fix content/readability and controls.
6. **Scheduled Jobs + Kanban** — rebuild route-specific controls and status language.
7. **Motion/state layer** — dot loaders, LED states, sheets, tactile press.
8. **QA pass** — 390px mobile screenshots + console + no overflow.

---

## 9. What “done” means

V2 is done only when the product no longer feels like:

```txt
old WebUI + black theme + red accents
```

It must feel like:

```txt
a focused mobile-first OS command surface with NothingOS-inspired typography, dot/LED state language, and route-specific workflows.
```
