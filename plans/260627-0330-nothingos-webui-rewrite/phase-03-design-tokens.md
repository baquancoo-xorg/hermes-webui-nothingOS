---
phase: 3
title: "Design tokens"
status: completed
priority: P1
dependencies: [2]
---

# Phase 3: Design tokens

## Overview
Định nghĩa token NothingOS theo spec mục 4 (color/typography/grid/surface/dot/motion) làm nguồn chân lý cho toàn bộ styling. Map sang biến CSS hiện có (`--bg`, `--surface`, `--accent`, `--border`...) mà JS/CSS đang dùng để không vỡ.

## Requirements
- Functional: 1 nguồn token ở `:root` (dark-only). Token reference (mục 4.1-4.6) có đủ.
- Non-functional: token cũ (`--accent`, `--border2`...) alias sang token mới để CSS hiện hữu vẫn chạy trong lúc chuyển tiếp.

## Architecture
Spec tokens (mục 4): `--os-bg #0b0b0a`, `--os-panel #161613`, `--os-raised #24241f`, `--os-text #f2f0e8`, `--os-muted #8b877b`, `--os-line rgba(242,240,232,.13)`, `--os-dot rgba(242,240,232,.16)`, `--os-red #ff3b30`. Typography: `--font-ui` (Geist/system sans), `--font-mono`, `--font-dot` (CSS/SVG dot, không font lậu). Grid 8px, radius 10-32px (industrial, không pill). Motion: `--ease-os cubic-bezier(.16,1,.3,1)`, dur 120/220/700ms.

**Alias map** (token cũ → mới) để CSS legacy không vỡ:
`--bg→--os-bg`, `--surface→--os-panel`, `--text→--os-text`, `--muted→--os-muted`, `--border→--os-line`, `--accent→--os-red`...

## Related Code Files
- Create: `static/tokens.css` (load trước style.css trong index.html)
- Modify: `static/index.html` (thêm `<link rel="stylesheet" href="/static/tokens.css">` trước style.css)
- Modify: `static/style.css` (`:root` của skin `nothingos` trỏ alias sang tokens)

## Implementation Steps
1. Tạo `tokens.css` với toàn bộ token spec mục 4.1-4.6.
2. Font: dùng Geist/Geist Mono nếu có sẵn trong `static/vendor`/dist font; nếu không → system-ui sans + JetBrains Mono (đã có trong dist fonts) làm fallback. KHÔNG font dot lậu — dot effect bằng CSS (Phase 6).
3. Trong `style.css` `:root[data-skin="nothingos"]`, set alias biến cũ = biến mới.
4. Bỏ pill default + neon glow ở token (radius mặc định industrial; shadow = inset subtle, không glow).
5. Link tokens.css vào index.html trước style.css.

## Success Criteria
- [ ] `tokens.css` chứa đủ token mục 4.1-4.6.
- [ ] Biến cũ (`--accent`, `--surface`...) resolve sang token mới, CSS legacy không vỡ visual nghiêm trọng.
- [ ] Không còn neon glow / pill mặc định trong token.
- [ ] Không nhúng font lậu; dot dùng CSS.

## Risk Assessment
- **Risk:** alias sai làm lệch màu hàng loạt. **Mitigation:** map từng biến, screenshot so sánh.
- **Risk:** font Geist không có license/asset. **Mitigation:** fallback system-ui + JetBrains Mono (đã có trong repo).
