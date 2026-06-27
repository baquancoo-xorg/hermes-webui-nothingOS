---
phase: 4
title: "Tái cấu trúc shell (layout)"
status: completed
priority: P1
dependencies: [3]
---

# Phase 4: Tái cấu trúc shell (layout)

## Overview
Tái cấu trúc layout grid của `static/index.html` theo reference: ambient strip (top) + 3 cột (OS rail / agent surface / glance widgets) + quick command tray (bottom). Pixel-perfect khung shell. Giữ nguyên mọi `id` JS.

## Requirements
- Functional: layout grid khớp reference (`grid-template-rows: auto 1fr auto`; cột `236px minmax(420px,1fr) 318px`). Chat surface (`#mainChat`, `#messages`, `#composerBox`) nằm đúng cột giữa, hoạt động như cũ.
- Non-functional: responsive theo reference media queries (1100px → ẩn widgets/thu rail; 720px → 1 cột).

## Architecture
Layout hiện tại: `.layout` chứa `.rail` + `.sidebar` + `#mainChat` (2 cột). Reference: 3 vùng dọc + 3 cột ngang.

**Cách bọc (không đổi id):**
- Thêm wrapper `.os-app` (grid 3 hàng) bao ngoài `.layout`.
- Hàng 1: `.os-ambient` (Phase 5).
- Hàng 2: `.os-shell` grid 3 cột:
  - Cột trái: tái dùng `.sidebar`/`.rail` → style thành OS rail.
  - Cột giữa: `#mainChat` + `.messages-shell` + `.composer-wrap` (giữ nguyên id).
  - Cột phải: `.os-widgets` (Phase 5) — vùng mới, hoặc tái dùng `.rightpanel` nếu tồn tại.
- Hàng 3: `.os-quick` quick tray (Phase 5).

Reference grid là khung xương; nội dung Hermes (session list, workspace panel) map vào rail/cột.

## Related Code Files
- Modify: `static/index.html` (bọc wrapper layout, giữ id; thêm placeholder ambient/widgets/quick)
- Modify: `static/style.css` (grid `.os-app`/`.os-shell`/responsive; surface treatment cột)
- Reference: `ref/nothingos-webui-reference.html` (grid values, media queries dòng 22-76)

## Implementation Steps
1. Audit toàn bộ `id` trong vùng `.layout` → danh sách phải giữ.
2. Bọc `.os-app` + `.os-shell` quanh DOM hiện có; chèn placeholder `<section class="os-ambient">`, `<aside class="os-widgets">`, `<section class="os-quick">` (rỗng, fill ở Phase 5).
3. Port grid values từ reference (rows/cols/gap/padding).
4. Map `.sidebar` → OS rail style (active item dùng red index bar trái, không blue highlight).
5. Port 2 media query (1100/720px) từ reference.
6. Áp `.os-surface` (gradient + border + inset shadow, không drop shadow nặng) cho 3 cột.

## Success Criteria
- [ ] Desktop 1440px: 3 cột + ambient + quick tray khớp reference về tỉ lệ/spacing (pixel-perfect shell).
- [ ] Mọi `id` JS giữ nguyên; chat/session/composer hoạt động.
- [ ] 1100px: widgets ẩn, rail thu gọn. 720px: 1 cột, rail ẩn, composer là chính.
- [ ] Không drop shadow nặng; depth bằng border + nested panel.

## Risk Assessment
- **Risk:** bọc wrapper làm vỡ CSS selector con (`.layout > .sidebar`). **Mitigation:** kiểm tra selector con trước khi chèn wrapper; ưu tiên thêm class thay vì đổi cây.
- **Risk:** `#mainChat` mất chiều cao khi đổi grid. **Mitigation:** test scroll messages + composer sticky.
