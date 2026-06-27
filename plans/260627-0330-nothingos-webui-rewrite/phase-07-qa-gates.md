---
phase: 7
title: "QA gates"
status: completed
priority: P1
dependencies: [5, 6]
---

# Phase 7: QA gates

## Overview
Chạy QA checklist spec mục 10: visual, functional, technical. Xác nhận acceptance criteria toàn plan trước khi handoff/ship.

## Requirements
- Functional: login/session/chat/composer/tool-states/attachments chạy đúng.
- Non-functional: console 0 lỗi; contrast pass; mobile không overflow; single skin không thoát được.

## Architecture
Backend Python thuần — không có `npm run build/lint`. QA chủ yếu runtime + visual. **[Validated S1]** Claude tự chạy `bootstrap.py` local → curl `/health` + screenshot desktop (1440px) / mobile (390px) để kiểm pixel-perfect vs reference.

## Related Code Files
- Verify-only: toàn bộ static/ + routes.py (không sửa logic mới ở phase này, chỉ fix regression)

## Implementation Steps
1. **localStorage guard:** set `hermes-skin=sienna`, `hermes-theme=light` → hard reload → vẫn NothingOS dark.
2. **Desktop screenshot 1440px** → so reference (shell pixel-perfect).
3. **Mobile screenshot 390px** → 1 cột, không overflow, composer là chính.
4. **Functional sweep:** login → session list → new chat → stream token → tool call render → attachment → composer submit.
5. **Console:** 0 uncaught error.
6. **Contrast:** body text vs bg đạt WCAG AA (os-text trên os-bg/panel).
7. **Settings:** xác nhận không lộ skin/theme picker.
8. **Keyboard nav:** tab qua rail/composer/tray.
9. **Technical:** `rg "sienna|data-skin=\"(ares|neon|...)\""` sạch; `frontend/dist` đã xoá; không secret commit; không ảnh copyright nhúng.

## Success Criteria
- [ ] 6 acceptance criteria của plan.md đều pass.
- [ ] QA checklist spec mục 10 (visual/functional/technical) tick hết.
- [ ] Console 0 lỗi; contrast AA; mobile clean.
- [ ] localStorage cũ không thoát NothingOS.

## Risk Assessment
- **Risk:** không có CI build → bỏ sót regression JS. **Mitigation:** functional sweep thủ công đủ path chính; ưu tiên login/stream.
- **Risk:** môi trường local không chạy được `bootstrap.py` (thiếu engine/dep). **Mitigation:** thử chạy sớm ở Phase 1; nếu blocker → báo Sếp QA trên staging.

<!-- Updated: Validation Session 1 - QA env = Claude tự chạy bootstrap.py + screenshot -->
