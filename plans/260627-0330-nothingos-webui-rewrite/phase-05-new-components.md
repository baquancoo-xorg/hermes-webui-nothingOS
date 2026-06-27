---
phase: 5
title: "3 thành phần mới + JS feed"
status: completed
priority: P2
dependencies: [4]
---

# Phase 5: 3 thành phần mới + JS feed

## Overview
Hiện thực 3 thành phần reference chưa có ở v1: AmbientStatusStrip, GlanceWidgets, QuickCommandTray. Feed dữ liệu từ state JS có sẵn (không tạo API mới — YAGNI).

## Requirements
- Functional:
  - **AmbientStatusStrip:** state machine idle/thinking/tool_running/waiting_approval/error/complete (spec mục 6) — visual theo bảng.
  - **GlanceWidgets:** Current Run, Memory mode, Glyph-like signal (theo reference); mở rộng Tools/Approvals/Git nếu có data.
  - **QuickCommandTray:** tiles Model/Profile/Tools/Memory/Cron/Safety/Workspace (+Skin=locked) với state off/on/active/warning/blocked.
- Non-functional: animation chỉ opacity/transform/background-position (spec mục 4.6); reduced-motion tôn trọng.

## Architecture
- **Ambient:** 1 element `.os-ambient .pulse`; class `data-state` đổi theo agent state. Hook vào điểm v1 đã biết trạng thái stream (SSE handler trong `messages.js`/`sessions.js` — nơi set tool-running/approval). Không thêm API; đọc state hiện có.
- **Widgets:** đọc state có sẵn — session count/turns, model, branch (workspace_git), pending approvals, memory mode. Render mono metric như reference (`.metric`, `.mini-grid`).
- **Quick tray:** mỗi tile đọc giá trị từ state đang hiển thị ở composer footer (model chip, profile chip, workspace chip đã tồn tại) → tile là view gọn + click mở control tương ứng (tái dùng handler chip có sẵn).

## Related Code Files
- Modify: `static/index.html` (markup 3 vùng từ Phase 4 placeholder)
- Modify: `static/style.css` (style + keyframes sweep/slide/ripple từ reference dòng 24-72)
- Modify: `static/messages.js` / `static/sessions.js` (emit agent state → ambient; đọc-only, không đổi logic stream)
- Create (nếu cần tách): `static/os-widgets.js` (feed widgets/tray, ~<200 dòng)

## Implementation Steps
1. Markup 3 vùng theo reference (ambient strip; 3 widget; 8 quick tile).
2. CSS: port keyframes `sweep`/`slide` + state classes ambient (bảng mục 6).
3. Ambient feed: tìm điểm set trạng thái tool/approval trong stream handler → set `osAmbient.dataset.state`. Mapping: thinking khi chờ token, tool_running khi tool call, waiting_approval khi pending, error/complete tương ứng.
4. Widgets feed: hàm `renderGlance()` đọc state (session turns, model, branch, approvals) → cập nhật khi session đổi.
5. Quick tray: bind mỗi tile vào chip/control sẵn có (model→model picker, workspace→workspace panel...). Tile Skin = `locked`, không click.
6. Reduced-motion: tắt animation.

## Success Criteria
- [ ] Ambient đổi visual đúng 6 state khi chat thật (thinking/tool/approval/error/done).
- [ ] Widgets hiển thị số liệu thật (turns/model/branch/approvals), cập nhật khi đổi session.
- [ ] Quick tile click mở đúng control; state (on/active/warning) phản ánh thực tế.
- [ ] Không tạo API mới; animation chỉ opacity/transform.

## Risk Assessment
- **Risk:** không tìm đúng điểm state trong stream handler. **Mitigation:** scout `messages.js` SSE trước; nếu khó, bám sự kiện DOM tool-card đã có.
- **Risk:** tray duplicate logic chip. **Mitigation:** tái dùng handler chip, không viết lại (DRY).
