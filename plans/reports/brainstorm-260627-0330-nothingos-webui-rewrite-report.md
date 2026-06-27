# Brainstorm — NothingOS-inspired Hermes WebUI Rewrite

> Date: 2026-06-27 · Mode: brainstorm (no flags) · Status: design approved, ready for `/ck:plan`

## 1. Problem statement & requirements

Tái thiết kế **toàn bộ** Hermes WebUI theo design language NothingOS-inspired (1 skin duy nhất, monochrome-first, dot-matrix, widget-first, ambient status), pixel-perfect với `ref/nothingos-webui-reference.html` cho shell chính.

**Exact requirements (đã chốt qua Discovery):**
- **Expected output:** Toàn bộ WebUI render theo design system NothingOS. Shell chính (ambient strip + OS rail + agent surface + glance widgets + quick command tray) pixel-perfect với reference. Route `/` serve v1 `static/`. v2 `frontend/dist` bị xoá.
- **Acceptance criteria:**
  1. Shell khớp reference: 3-cột + ambient strip top + quick tray bottom.
  2. Chỉ 1 skin `nothingos`; settings KHÔNG còn skin/theme picker.
  3. Reload với `localStorage['hermes-skin']='sienna'` (hoặc theme cũ) vẫn render NothingOS.
  4. Login / session list / chat stream / composer submit / tool-call states chạy như cũ.
  5. Console errors = 0; body text contrast đạt; mobile 390px không overflow.
- **Scope boundary (OUT):** Không sửa backend API logic; không thêm feature mới; không dựng React/Vite; không pixel-match các màn phụ (không có ảnh mẫu).
- **Touchpoints:** `static/index.html`, `static/style.css`, `static/boot.js` (theme/skin logic), `api/routes.py` (route `/`), `api/frontend_v2.py` (xoá), `frontend/dist/` (xoá), `static/ui.js` (settings picker).

## 2. Codebase findings (scouted)

| Phát hiện | Hệ quả |
|---|---|
| **2 frontend song song.** `static/` = v1 vanilla JS (~56k dòng, source thật, đã nối API). `frontend/dist/` = v2 React SPA **minified 823KB, KHÔNG có source** ở bất kỳ repo nào (kể cả upstream Tungbillee & gốc nesquena). | v2 là ngõ cụt. v1 là nền tảng rewrite. |
| Route `/` → redirect `/v2/` khi logged-in (`routes.py:4724`). | Phải đổi để serve v1 static, hoặc cho static thành SPA chính. |
| Commit `ace6b5b` "NothingOS theme" = **CSS overlay** `[data-skin="nothing"]` + `!important`, dùng `border-radius:999px` (pill) + neon red glow `box-shadow:0 0 28px rgba(255,0,51,.28)`. | Đúng 2 anti-pattern spec mục 8. Phải gỡ, không kế thừa. |
| **15 skins** trong `style.css` + theme system (localStorage `hermes-skin`/`hermes-theme` + server sync `boot.js:1770-1795`). | Spec P0: gỡ 14 skin + picker, hardcode `nothingos`, thêm migration guard. |
| Layout hiện tại **2 cột** (`.rail`+`.sidebar`+`#mainChat`). Thiếu ambient strip, glance widgets, quick tray. | 3 thành phần phải thêm mới. |
| JS 56k dòng bám chặt `id` (`#messages`, `#composerBox`, `#sessionList`...). | Giữ nguyên id → không vỡ logic. |
| Backend Python thuần (HTTP handler tự viết), API contract độc lập frontend. | Rewrite UI không đụng backend logic. |

**Repo lineage (verified):** `nesquena/hermes-webui` (gốc, vanilla, có source) → `Tungbillee/hermes-webui` (thêm v2 dist, không source) → repo này.

## 3. Evaluated approaches

| | A — Token-only CSS | B — Shell mới từ 0 | **C — Hybrid (CHỌN)** |
|---|---|---|---|
| Cách làm | Giữ DOM 2 cột, chỉ thay CSS | Viết lại index.html + map lại JS | Giữ id, tái cấu trúc layout + rewrite design system |
| Pixel-perfect | ❌ Không (thiếu ambient/widgets/tray) | ✅ | ✅ |
| Rủi ro JS | Thấp | **Rất cao** (vỡ login/streaming) | Trung bình |
| Công sức | Thấp | **Cao nhất** | Trung bình |
| Đúng spec? | ❌ Giống overlay bị chê | ✅ | ✅ |
| Verdict | Loại | Loại | **Chọn** |

## 4. Final solution — Cách C Hybrid

**Nguyên tắc:** Giữ mọi `id` JS đang dùng (không vỡ logic). Bọc lại layout grid theo reference. Rewrite design system. Gỡ sạch theme/skin cũ.

### Quyết định đã chốt
- **Nền tảng:** rewrite trên **v1 vanilla `static/`** (có source + API đã nối). Xoá v2 `frontend/dist`.
- **Phạm vi:** toàn bộ app.
- **Độ bám ref:** shell chính **pixel-perfect**; màn phụ **áp chung design system** (token/surface/dot/mono) — không pixel-match (không có ảnh mẫu).
- **v1 legacy:** gỡ bỏ 14 skin + picker, chỉ còn `nothingos`.

### Phase plan (chi tiết hoá ở `/ck:plan`)
1. **Gỡ theme system** — hardcode skin `nothingos`; migration guard (localStorage cũ → `nothingos`); bỏ skin/theme picker khỏi settings UI; xoá CSS 14 skin kia.
2. **Tokens** — `tokens.css` theo spec mục 4 (color/typography/grid/surface/dot/motion). Bỏ pill mặc định, bỏ neon glow.
3. **Tái cấu trúc shell** — thêm AmbientStatusStrip (top), OS Rail style cho sidebar, GlanceWidgets (cột phải), QuickCommandTray (bottom). Giữ id chat/composer/session.
4. **Rewrite component styling** — OS-surface, dot pseudo-element (opacity <.28, pointer-events none), state-driven strips. Xoá pill/neon (anti-pattern mục 8).
5. **3 thành phần mới + JS feed** — ambient state machine (idle/thinking/tool/approval/error/done), glance widgets data, quick tiles (Model/Profile/Tools/Memory/Cron/Safety/Workspace) từ state có sẵn.
6. **Routing + dọn v2** — `/` serve static; xoá `frontend/dist` + `api/frontend_v2.py` + nhánh `/v2/` trong routes.
7. **QA** — reload localStorage cũ; screenshot 1440px & 390px; console 0 lỗi; contrast; keyboard nav.

## 5. Implementation considerations & risks

- **Risk: `style.css` 5.335 dòng** đan xen 15 skin. Gỡ phải cẩn thận tránh xoá nhầm base style. → Cô lập block skin theo selector `[data-skin="..."]`, giữ base.
- **Risk: JS bám id.** Tái cấu trúc DOM chỉ được *bọc thêm wrapper / đổi class*, **không đổi/ xoá id**. → Audit id trước khi sửa.
- **Risk: 3 thành phần mới cần data động.** Tận dụng state JS hiện có (model, profile, tools, session count, branch). Không tạo API mới (YAGNI).
- **Risk: route switch** có thể vỡ deep-link `/session/...` đang trỏ v2. → Map sang shell static.
- **Pixel-perfect chỉ cho shell chính** — đã thống nhất, ghi rõ để tránh kỳ vọng sai ở màn phụ.

## 6. Success metrics / validation

QA checklist spec mục 10: single visual language; không Sienna/Tungbillee residue; dot-matrix chỉ ở badge/status/widget; red chỉ cho critical; contrast pass; mobile không overflow; login/session/chat/composer/tool-states chạy; settings không lộ picker; localStorage cũ không thoát khỏi NothingOS; console 0 lỗi.

## 7. Next steps & dependencies

- **Next:** `/ck:plan` với report path này để dựng phase chi tiết.
- **Dependency:** không (source v1 đầy đủ trong repo).

## 8. Unresolved questions

- Có cần giữ `api/frontend_v2.py` cho rollback tạm thời không, hay xoá hẳn ngay? (đề xuất: giữ 1 commit rồi xoá ở commit riêng để dễ revert).
- Route `/session/<id>` deep-link: client router của static có handle path này không, hay cần thêm? (kiểm tra ở Phase 6).
