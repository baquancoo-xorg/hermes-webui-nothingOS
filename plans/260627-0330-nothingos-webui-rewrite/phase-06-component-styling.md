---
phase: 6
title: "Rewrite component styling + màn phụ"
status: completed
priority: P2
dependencies: [4]
---

# Phase 6: Rewrite component styling + màn phụ

## Overview
Rewrite styling các component (message, composer, session item, tool card, button, input) sang design system NothingOS. Áp chung design system cho màn phụ (settings/onboarding/terminal/kanban/workspace) — không pixel-match. Xoá anti-pattern (pill, neon glow, dot everywhere).

## Requirements
- Functional: mọi component dùng os-surface/dot/state-strip/mono đúng spec mục 6. Màn phụ nhất quán visual.
- Non-functional: dot pseudo-element opacity <.28, pointer-events none; red chỉ cho critical; body text không dùng dot font.

## Architecture
Component spec (mục 6):
- **AgentSurface:** user = right/raised panel; assistant = left/ít boxed; tool call = collapsible mono header; error = red left rail.
- **Composer:** command-line feel, placeholder ngắn, mono glyph button, focus = white border + red corner marker (KHÔNG glow). Không dot sau input text.
- **OSRail:** icon+label mono, active = red index bar trái.
- Buttons: industrial radius (không pill 999px), mono uppercase label.

Anti-pattern phải xoá (mục 8): pill everywhere, red border mọi card, neon glow, dot background everywhere, dot font cho body.

Màn phụ: áp token + os-surface + dot accent ở heading/badge; giữ chức năng, đổi vỏ.

## Related Code Files
- Modify: `static/style.css` (rewrite block component; xoá overlay ace6b5b)
- Reference: `ref/nothingos-webui-reference.html` (style từng component)
- Touch: settings/onboarding/terminal/kanban/workspace CSS section trong style.css

## Implementation Steps
1. Rewrite message (`.msg-row`, `.msg-body`): user raised, assistant content block, radius industrial (không 22px pill).
2. Rewrite composer (`.composer-box`): focus white border + red corner, bỏ neon glow + dot strip trái (overlay cũ).
3. Rewrite session item (`.session-item.active`): red index bar trái, bỏ glow.
4. Tool card: collapsible mono header, running = segmented strip (không neon dot glow).
5. Button/input: industrial radius, mono label, bỏ pill 999px.
6. Màn phụ: sweep từng section, áp os-surface + token; heading mono + dot accent. Không pixel-match.
7. Grep xoá residue: `border-radius:999px`, `0 0 28px rgba(255,0,51`, dot background toàn cục.

## Success Criteria
- [ ] Không còn pill 999px / neon glow trong style.css (grep sạch).
- [ ] Dot chỉ ở badge/status/widget; body text không dot.
- [ ] Red chỉ xuất hiện ở critical state/action.
- [ ] Màn phụ nhất quán design system, chức năng nguyên vẹn.
- [ ] Contrast body text đạt WCAG AA.

## Risk Assessment
- **Risk:** style.css 5.335 dòng — sweep sót section. **Mitigation:** liệt kê section theo panel-view id, tick từng cái.
- **Risk:** đổi radius/spacing vỡ layout component con. **Mitigation:** screenshot trước/sau từng nhóm.
