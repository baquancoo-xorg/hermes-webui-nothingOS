---
title: "Brainstorm — Light Mode + Mobile UX + Workspace Preview Access"
date: 2026-06-27
type: brainstorm
status: approved
branch: main
related_commit: c82e2f9 (NothingOS rewrite)
---

# Brainstorm: Light Mode + Mobile UX + Workspace Preview

3 việc Sếp giao, gói chung 1 round. Approach **A — Surgical** (tái dùng tối đa code có sẵn).

## Problem statement

1. **Light Mode** — rewrite trước ép single dark skin; Sếp muốn thêm lại toggle Light/Dark (vẫn NothingOS).
2. **Workspace preview** — Sếp tưởng "chưa có"; thực tế ĐÃ CÓ ĐẦY ĐỦ. Gốc vấn đề: **mobile không mở được panel workspace**.
3. **Mobile UX** — quick tray mới ăn ~300px đáy; cần audit 390px.

## Scout findings (key facts)

- Stack: Python backend serve static vanilla-JS SPA. Không framework. `style.css` ~4800 dòng, `tokens.css` (--os-* dark-only).
- Preview ĐÃ CÓ: `ui.js:9455` file row `onclick → openFile()` → `workspace.js:637` render `.md`/ảnh/pdf/html/code/media. **Hoạt động trên desktop.**
- **Mobile preview root cause:** CSS mâu thuẫn 2 tầng —
  - `@media 900px`: `.rightpanel{display:none}`
  - `@media 640px`: `.rightpanel{position:fixed;right:-300px}` + `.rightpanel.mobile-open{right:0}` (overlay drawer ĐÃ CÓ)
  - JS `boot.js:145` toggle `.mobile-open` qua `openWorkspacePanel()` ĐÃ CÓ
  - **NHƯNG nút mở (`.mobile-files-btn`/`.workspace-toggle-btn`) CSS dựng nhưng KHÔNG có trong `index.html`** → mobile không có cách mở. Khoảng 640–900px thì `display:none` thắng.
- Light mode: `_normalizeAppearance` (boot.js:1503) ép cứng `dark`; pre-paint (index.html:22) ép dark; base `style.css` còn 107 rule `:root:not(.dark)` (light cũ, màu Tungbillee — KHÔNG tái dùng cho NothingOS light).
- Quick tray mobile: 8 tile × 2 cột = 4 hàng ≈ 300px.

## Approaches evaluated

| | A — Surgical (CHỌN) | B — Full rebuild light |
|---|---|---|
| Light | Thêm block `:root.light[data-skin=nothingos]` đảo --os-* token | Viết lại mọi component cho light |
| Effort | Thấp | Cao (×3) |
| Risk | Thấp, tái dùng | Cao, dễ vỡ |
| YAGNI/DRY | ✅ | ❌ over-engineer |

→ **Approach A.**

## Final design (approved)

### Task 1 — Light Mode (toggle Light/Dark, default Dark)
- `tokens.css`: thêm block light variant — đảo `--os-bg/panel/text/muted/line/dot` sang nền sáng, **giữ `--os-red` accent + dot identity**. Định nghĩa dưới `:root.light` (hoặc `html:not(.dark)`).
- `boot.js`: `_normalizeAppearance` cho phép `{theme: light|dark, skin: nothingos}` (bỏ ép cứng dark, vẫn ép skin=nothingos). `_applyTheme` add/remove class `.light`/`.dark`.
- Pre-paint (`index.html:22`): đọc `hermes-theme` (default `dark`), set class tương ứng — bỏ ép dark vô điều kiện.
- Settings→Appearance: thêm lại block 2 nút Light/Dark (gọn, không phải 16-skin picker cũ). `_pickTheme` chỉ nhận light/dark.
- Theme-color meta sync light/dark.
- **Contrast: test lại toàn bộ component ở light (WCAG AA).**

### Task 2 — Workspace preview access trên mobile
- Thêm nút "Files" vào mobile (composer mobile-config hoặc topbar) → gọi `openWorkspacePanel('browse')` (tái dùng, KHÔNG viết mới).
- Dọn mâu thuẫn breakpoint: bỏ `.rightpanel{display:none}` ở 900px, để overlay drawer (`mobile-open`) chạy thống nhất từ ≤900px.
- Style overlay drawer theo os-surface (NothingOS).
- KHÔNG đụng `openFile()`/`showPreview()` (đã chạy tốt).

### Task 3 — Mobile UX 390px
- **Quick tray**: mobile → 1 hàng scroll ngang (overflow-x:auto) thay 4 hàng 300px. Tiết kiệm đáy màn hình.
- **Ambient strip / OS rail / composer**: audit 390px — không overflow, touch target ≥40px.
- Test light + dark đều ở mobile.

## Touchpoints
- `static/tokens.css` (light token block)
- `static/boot.js` (`_normalizeAppearance`, `_applyTheme`, `_pickTheme`)
- `static/index.html` (pre-paint script, Appearance toggle, mobile Files button)
- `static/style.css` (light component rules, quick tray mobile, rightpanel breakpoint cleanup)
- `static/commands.js` (`cmdTheme` cho phép light/dark lại)

## Out of scope
- KHÔNG khôi phục 14 skin cũ (chỉ Light/Dark của nothingos).
- KHÔNG viết lại preview engine (đã có).
- KHÔNG đụng backend.
- KHÔNG System/auto-OS theme (chỉ Light/Dark thủ công).

## Acceptance criteria
1. Settings→Appearance có 2 nút Light/Dark; đổi đổi màu ngay, lưu localStorage, reload giữ.
2. Default lần đầu = Dark; localStorage cũ vẫn ép skin=nothingos.
3. Light mode: nền sáng + chữ tối + đỏ accent + dot; contrast AA.
4. Mobile (≤900px): có nút mở workspace → file browser → click file → preview .md/ảnh/pdf hiện trong drawer.
5. Quick tray mobile không ăn >1 hàng; ambient/rail/composer 390px không overflow.
6. Console 0 lỗi; desktop dark vẫn như cũ (không regression).

## Risks
- Light contrast sót chỗ (component hardcode dark hex) → audit screenshot light.
- Breakpoint cleanup vỡ desktop rightpanel → test cả desktop + mobile.
- Reduced-motion + theme class tương tác → kiểm tra.

## Verify plan
Em tự test live (Orca browser): toggle light/dark desktop + mobile, preview file mobile, screenshot, commit, báo 1 lần.

## Open questions
- None — đã chốt ở 2 round AskUserQuestion.
