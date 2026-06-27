# NothingOS-inspired Hermes WebUI Rewrite Spec

> **Purpose:** Research + design spec để Dominium đưa ClaudeCode làm lại Hermes WebUI theo hướng NothingOS-inspired.  
> **Date:** 2026-06-26  
> **Scope:** WebUI cho Hermes Agent/CoWorkOS. Không sao chép logo/font/asset độc quyền của Nothing. Chỉ chuyển hoá nguyên lý UI/UX công khai thành design language riêng.  
> **Output companion:** `artifacts/design/nothingos-webui-reference.html`

---

## 0. TL;DR

Bản hiện tại vẫn giống “skin phủ lên Tungbillee UI”. Hướng đúng cho rewrite là **single design system**, không có theme switcher/fallback:

1. **Một skin duy nhất:** NothingOS-inspired. Không còn lựa chọn màu khác, không còn Sienna/legacy palette.  
2. **Monochrome-first:** đen/trắng/xám, accent đỏ rất tiết chế.  
3. **Widget-first workspace:** UI như home/lock/dashboard của OS: nhiều module glanceable, không phải web app card generic.  
4. **Dot-matrix có kiểm soát:** dùng cho heading nhỏ, badge, counter, status strip, animation; không dùng cho body text dài.  
5. **Quick Settings as command tray:** model/profile/tools/workspace/plugins là các control tiles có trạng thái.  
6. **Glyph-inspired ambient state:** agent thinking/tool-running/error/success thể hiện bằng light strip/pulse/progress, không clone glyph shape.  
7. **Remove Tungbillee residue:** xoá theme picker, token cũ, radii/shadow/card style cũ, layout shell cũ nếu nó quyết định visual hierarchy.

---

## 1. Source pack & provenance

| Source | Type | Key evidence | Design implication |
|---|---|---|---|
| Nothing Icon Pack — Google Play: https://play.google.com/store/apps/details?id=com.nothing.icon | 🔵 #external-verified / official store listing | Listing text: “monochrome colour scheme”, “Match app icons to your Nothing widgets”, “reduce distractions”, “interactions ... more intentional”. | Iconography phải mono; UI nên ít màu, giảm nhiễu, ưu tiên intention over decoration. |
| Nothing Phone (4a) product page: https://nothing.tech/products/phone-4a | 🔵 #external-verified / official product page | Page text includes “Nothing OS with Essential AI tools”; disclaimer mentions “Live Updates with Glyph Progress”. | OS identity gắn với AI tools + live progress/ambient signal. Hermes cần progress language rõ cho agent/tool. |
| Nothing Glyph Mirror: https://nothing.tech/glyph-mirror | 🔵 #external-verified / official interactive page | Page text: “Create your custom glyph mirror.” | Glyph là custom ambient/light language; web adaptation nên là light bars/rhythm, không copy hardware glyph. |
| Nothing Community — OS 3.0 Open Beta for Phone (1): https://nothing.community/en/d/22248-nothing-os-30-open-beta-1-for-nothing-phone-1 | 🔵 #external-verified / official community | Changelog lists Shared Widgets, Lock screen, expanded widget space, Smart Drawer, Quick Settings redesign, enhanced widget library, pop-up view, dot-matrix fingerprint/charging animations. | Build primitives: widgets, lock/glance layout, smart grouping, quick settings tray, floating pop-up panels, dot animation tokens. |
| Nothing Community — Lock Screen & Quick Settings setups: https://nothing.community/d/18921-nothing-os-30-lock-screen-quick-settings-setups | 🔵 #external-verified / official community | Discusses “new lock screen and quick settings panel”, new clocks, widget grid options, visual overhaul/customisation. Also notes contrast concerns in light widgets. | Support configurable grid layout but maintain single skin. Contrast must be tested; light mode not needed unless later. |
| Android Authority — Nothing OS 3.0 hands-on: https://www.androidauthority.com/nothing-os-3-hands-on-3488739/ | 🔵 #external-verified / editorial review | Title “Dot matrix re-reloaded”; notes dot-based widgets and dot font; unlock animation rippling dots; pedometer/screen-time/camera widgets remain dot-based; quick settings easier to reach/resize; brightness slider at bottom; smart drawer. | Dots should be a living system, not static background. Use resizeable tiles, bottom/near-composer controls for reachability. |
| Android Faithful — First look at Nothing OS 3.0: https://www.androidfaithful.com/nothing-os-3-0-hands-on/ | 🔵 #external-verified / technical review | Details redesigned notifications/Quick Settings, 2x1 tiles with extra states, brightness slider, lock screen customization preview, 4x2/4x4 widget grids, widget picker with Nothing widgets first, pop-up view windows minimized/pinned. | Use stateful tiles, previewable layouts, dedicated internal widget library, floating/minimizable panels for tools/sessions. |

### Source quality notes

- Some legacy Nothing blog URLs redirected/404 through the current Shopify/Oxygen site. I did **not** rely on dead-page wording as verified quotes.  
- Nothing Community is official/community-hosted but includes user comments; treat official changelog sections as stronger than comments.  
- External review screenshots are useful as reference links, but implementation should use CSS-generated patterns instead of copying images/assets.

---

## 2. Design DNA extracted from NothingOS

### 2.1 Monochrome intentionality

**Signal:** Official Icon Pack says monochrome scheme matches widgets and reduces distractions.  
**WebUI rule:**

- Default background: off-black or off-white; for Hermes use **dark-first** because command/chat context benefits from low glare.
- Accent color budget: one red accent only.
- No blue/purple AI gradient, no multicolor app icons.
- Icons are line/solid mono, same optical weight.

### 2.2 Widget-first system

**Signal:** Nothing OS uses widgets on home/lock screen, expanded widget areas, dedicated Nothing widget picker.  
**WebUI rule:**

- Home screen = operating dashboard, not a marketing page.
- Every major function maps to a widget/tile: conversation, model/provider, tool activity, workspace, Git/service status, cron jobs, memory/context, pending approvals.
- Widgets must be glanceable: short label, one primary metric/status, one action.

### 2.3 Dot-matrix identity

**Signal:** Android Authority observed dot-based widgets/font; official changelog mentions dot matrix fingerprint/charging animations.  
**WebUI rule:**

- Use dots for identity and state, not body copy.
- Good use: eyebrow labels, timestamp/counter badges, loading/state strips, empty-state illustration, lock/glance widget patterns.
- Bad use: long paragraphs, input placeholders, dense table rows.

### 2.4 Quick Settings as command layer

**Signal:** Nothing OS 3.0 redesigned Quick Settings, resizable tiles, reachable brightness slider, extra tile states.  
**WebUI rule:**

- Hermes should have a **Quick Command Tray** for model, profile, workspace, toolset, memory, browser/terminal, cron, safety/approval.
- Tiles support sizes: `1x1`, `2x1`, `2x2`.
- Expanded tile reveals exact controls, not a modal maze.
- Critical controls live near composer/bottom rail for reachability.

### 2.5 Glyph-inspired ambient state

**Signal:** Nothing product/Glyph language uses live progress/ambient light; official page mentions Glyph Progress live updates.  
**WebUI rule:**

- Agent state should be ambient, not noisy:
  - Idle: dim static line
  - Thinking: slow dot ripple
  - Tool running: segmented progress strip
  - Waiting approval: red breathing marker
  - Error: short red pulse + inline message
  - Done: white sweep, then settle
- Do not copy hardware Glyph shapes. Use generic light strips/rhythms.

### 2.6 Smart grouping

**Signal:** Official changelog mentions AI-powered Smart Drawer auto-categorising apps.  
**WebUI rule:** group sessions/tools/workspaces by intent: active now, needs approval, recently touched, automation/cron, knowledge/memory.

---

## 3. Non-negotiable implementation principles

### P0 — Single skin only

ClaudeCode must remove/disable all theme switching in this fork.

Required:

```txt
- Remove skin dropdown from settings UI.
- Remove theme/color choices that can revert to Tungbillee visual style.
- Hardcode/centralize tokens in one CSS design system.
- If localStorage has old theme/skin, ignore or migrate to `nothingos`.
- CSS must not depend on `[data-skin="sienna"]`, `[data-theme="light"]`, etc.
- Any remaining theme data structures must expose exactly one option: `nothingos`.
```

Acceptance:

```js
localStorage.setItem('theme', 'light')
localStorage.setItem('skin', 'sienna')
// reload => UI must still render NothingOS-inspired dark skin.
```

### P0 — No cosmetic overlay on old UI

Do not just append CSS overrides on Tungbillee class names. Rewrite the visible shell structure if needed.

Bad:

```css
.old-card { background: black; border: red; }
```

Good:

```txt
AppShell
  OSRail
  GlanceWidgets
  AgentSurface
  QuickCommandTray
  AmbientStatusStrip
```

### P0 — No copyright/trademark copying

- Do not use Nothing logo.
- Do not include official product images in repo.
- Do not claim “official NothingOS UI”.
- Use wording: “NothingOS-inspired”, “monochrome mobile OS patterns”, “dot-matrix inspired”.

---

## 4. Design tokens

### 4.1 Color tokens

```css
:root {
  color-scheme: dark;
  --os-bg: #0b0b0a;
  --os-bg-2: #11110f;
  --os-panel: #161613;
  --os-panel-2: #1d1d19;
  --os-raised: #24241f;
  --os-text: #f2f0e8;
  --os-text-soft: #c9c5b8;
  --os-muted: #8b877b;
  --os-faint: #5b574e;
  --os-line: rgba(242,240,232,.13);
  --os-line-strong: rgba(242,240,232,.22);
  --os-dot: rgba(242,240,232,.16);
  --os-red: #ff3b30;
  --os-red-deep: #b81812;
  --os-red-soft: rgba(255,59,48,.14);
}
```

### 4.2 Typography

Recommended stack:

```css
--font-ui: "Geist", "Satoshi", "SF Pro Display", system-ui, sans-serif;
--font-mono: "Geist Mono", "JetBrains Mono", "SF Mono", ui-monospace, monospace;
--font-dot: "NDot-like", "Geist Mono", ui-monospace, monospace;
```

If no licensed dot font exists, build dot effect with CSS/SVG, not pirated fonts.

Rules:

- Body: readable UI sans.
- Numbers/status: mono.
- Dot typography: labels/counters/OS identity only.
- Eyebrow tracking: `0.18em–0.32em`.

### 4.3 Grid/spacing/radius

```css
--grid-unit: 8px;
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-6: 24px;
--space-8: 32px;
--space-12: 48px;
--radius-sm: 10px;
--radius-md: 16px;
--radius-lg: 24px;
--radius-xl: 32px;
```

NothingOS-inspired UI should feel precise/industrial, not bubbly. Avoid generic SaaS pill everywhere.

### 4.4 Surface treatment

```css
.os-surface {
  background:
    linear-gradient(180deg, rgba(255,255,255,.045), rgba(255,255,255,.015)),
    var(--os-panel);
  border: 1px solid var(--os-line);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.06);
}
```

Avoid heavy drop shadows. Depth comes from nested panels, subtle borders, dot texture, and hierarchy.

### 4.5 Dot texture

```css
.os-dot-grid {
  background-image: radial-gradient(circle, var(--os-dot) 1px, transparent 1px);
  background-size: 12px 12px;
}
```

Performance:

- Use pseudo-elements only.
- `pointer-events: none`.
- Opacity under `.28`.
- Do not animate the entire grid continuously.

### 4.6 Motion tokens

```css
--ease-os: cubic-bezier(.16, 1, .3, 1);
--ease-snap: cubic-bezier(.22, .61, .36, 1);
--dur-fast: 120ms;
--dur-ui: 220ms;
--dur-slow: 700ms;
```

Allowed animations: `opacity`, `transform`, small status strip background-position.  
Forbidden: layout-dimension loops, large scrolling blur, infinite heavy gradients.

---

## 5. Hermes WebUI information architecture

Desktop:

```txt
┌─────────────────────────────────────────────────────────────┐
│ Ambient Status Strip                                        │
├──────────────┬──────────────────────────────┬───────────────┤
│ OS Rail      │ Agent Conversation Surface   │ Glance Widgets │
│ sessions     │ message stream               │ task/status    │
│ workspace    │ composer                     │ memory/tools   │
├──────────────┴──────────────────────────────┴───────────────┤
│ Quick Command Tray / Control tiles                           │
└─────────────────────────────────────────────────────────────┘
```

Mobile:

```txt
Ambient strip → current session header → chat surface → composer → quick tray bottom sheet
```

Mobile requirements: no three-column layout, widgets collapse into horizontal scroll or bottom drawer, composer remains primary.

---

## 6. Component spec

### AmbientStatusStrip

| State | Visual | Behavior |
|---|---|---|
| idle | 1px dim white line | no motion |
| thinking | dot ripple center-out | slow loop |
| tool_running | segmented strip | label tool name |
| waiting_approval | red breathing block | noticeable |
| error | red pulse x2 then static edge | inline error text |
| complete | white sweep once | settle to idle |

### OSRail

- Icon + short label, monochrome only.
- Active item uses left red index bar or filled mono tile, not blue highlight.
- Session metadata in mono: `14:32 / 23 turns`.

### AgentSurface

- User: right/solid raised panel.
- Assistant: left/content block, less boxed.
- Tool call: collapsible technical module with mono header.
- Error: red left rail + concise message.

### Composer

- Large command-line feel.
- Placeholder short.
- Attach/send controls are mono glyph buttons.
- Focus state: white border + tiny red corner marker, not glow.
- No dot texture behind input text.

### QuickCommandTray

```ts
interface QuickTile {
  id: string;
  label: string;
  value: string;
  state: 'off' | 'on' | 'active' | 'warning' | 'blocked';
  size: '1x1' | '2x1' | '2x2';
  action: () => void;
}
```

Default tiles: Model, Profile, Workspace, Tools, Memory, Browser, Terminal, Cron, Approval.

### GlanceWidget

| Widget | Content | Inspiration |
|---|---|---|
| Current Task | task title/state/ETA | lock screen widget |
| Memory | source count/context mode | quick glance |
| Tools | active tool call/last result | control tile |
| Git/Service | branch/dirty/service status | live progress/glyph |
| Approvals | pending approvals | essential notification |
| Cron | next run/failures | widget grid |

### Pop-up panels

Use for tool detail, terminal panel, file preview, settings detail. Support minimize/pin. No giant modal for simple settings.

---

## 7. Concrete implementation tasks for ClaudeCode

### Phase 1 — Remove old theme system

1. Find all theme/skin definitions.
2. Replace with single `nothingos` token source.
3. Remove UI controls for choosing theme/skin.
4. Add migration guard: delete old `skin/theme` values or force `nothingos` on app boot.
5. Delete unused CSS branches.

Acceptance grep:

```bash
rg "sienna|skin|theme|data-theme|data-skin|light|dark" frontend static
```

Allowed only if `theme` means internal dark-only token; no visible theme selector remains.

### Phase 2 — Rebuild shell

Create new components:

```txt
src/ui/nothingos/
  tokens.css
  AppShell.tsx
  AmbientStatusStrip.tsx
  OSRail.tsx
  AgentSurface.tsx
  Composer.tsx
  QuickCommandTray.tsx
  GlanceWidget.tsx
  PopupPanel.tsx
```

If project is prebuilt dist only, reconstruct source or create clean frontend pipeline. Do **not** keep patching minified JS/CSS for final version.

### Phase 3 — Replace component styling

Remove generic SaaS card style. Use OS surface tokens, dot pseudo-elements, tile sizes, state-driven strips.

### Phase 4 — Interaction + states

Implement empty/loading/tool-running/pending-approval/connection-lost/mobile bottom tray.

### Phase 5 — QA gates

```bash
npm run build || true
npm run typecheck || true
npm run lint || true
```

Runtime QA: hard reload with old localStorage values, desktop screenshot 1440px, mobile screenshot 390px, console errors = 0, keyboard navigation, contrast check.

---

## 8. Anti-patterns to reject

| Anti-pattern | Why it fails |
|---|---|
| Existing Tungbillee UI with black/red CSS overlay | Still structurally ugly; does not become OS-like. |
| Theme picker still visible | Violates single-skin requirement. |
| Dot background everywhere | Visual noise. |
| Red borders on every card | Accent loses meaning. |
| Body text in dot font | Low readability. |
| Neon red glow | Too cyberpunk, not crisp/industrial. |
| Copy Nothing logo/font/assets | Legal/trademark risk. |
| Light/dark toggle | User explicitly wants one design language. |
| Generic 3-column SaaS card dashboard | Too template-like. |
| Multicolor brand icons | Breaks monochrome intentionality. |

---

## 9. ClaudeCode starter prompt

```txt
You are rewriting Hermes WebUI into a single NothingOS-inspired design system. Do not add a theme picker. Do not retain old Tungbillee/Sienna/light visual branches. Build one dark monochrome OS-like interface with dot-matrix accents, widget-first dashboard, quick-settings command tray, and glyph-inspired ambient status strips. Do not use Nothing logos/assets/fonts. Use the spec in docs/research/nothingos-webui-rewrite-spec.md and the standalone reference at artifacts/design/nothingos-webui-reference.html. First inspect current theme/skin code, remove fallback skins, then rebuild shell components and verify old localStorage theme values cannot change the UI away from NothingOS. Run build/typecheck/lint and provide desktop/mobile screenshots.
```

---

## 10. QA checklist

Visual:

- [ ] Single visual language everywhere.
- [ ] No Sienna/Tungbillee visual residue.
- [ ] Dot matrix used in badges/status/widgets only.
- [ ] Accent red appears only for critical state/action.
- [ ] Body text contrast passes.
- [ ] Mobile layout does not overflow.

Functional:

- [ ] Login/auth works.
- [ ] Session list works.
- [ ] Chat stream works.
- [ ] Composer submit works.
- [ ] Tool call states render.
- [ ] Attachments render.
- [ ] Settings do not expose theme switcher.
- [ ] Old localStorage skin/theme cannot escape the single design.

Technical:

- [ ] No minified-dist-only patching in final source.
- [ ] Build passes.
- [ ] Typecheck/lint pass or documented blockers.
- [ ] Console errors = 0.
- [ ] No private secrets committed.
- [ ] No external copyrighted images embedded.

---

## 11. Reference screenshot/source URLs to inspect manually

Use as visual references only; do not copy images into repo.

- Android Authority OS 3 hands-on: `https://www.androidauthority.com/nothing-os-3-hands-on-3488739/`
  - Lock screen: `https://www.androidauthority.com/wp-content/uploads/2024/10/Nothing-OS-3-lock-screen.jpg`
  - Widgets: `https://www.androidauthority.com/wp-content/uploads/2024/10/Nothing-OS-3-widgets.jpg`
  - Lock screen customization: `https://www.androidauthority.com/wp-content/uploads/2024/10/Nothing-OS-3-lock-screen-customization.jpg`
  - Smart drawer: `https://www.androidauthority.com/wp-content/uploads/2024/10/Nothing-OS-3-smart-drawer.jpg`
- Android Faithful deep dive screenshots: `https://www.androidfaithful.com/nothing-os-3-0-hands-on/`
- Nothing Community setup examples: `https://nothing.community/d/18921-nothing-os-30-lock-screen-quick-settings-setups`

---

## 12. Final decision summary

For Hermes WebUI rewrite, “NothingOS-inspired” should mean:

> A dark monochrome command OS, built from glanceable widgets and quick-setting tiles, with dot-matrix identity and ambient progress signals — not a reskinned chat app.
