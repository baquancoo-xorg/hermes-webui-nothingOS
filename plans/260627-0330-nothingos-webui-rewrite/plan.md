---
title: "NothingOS-inspired Hermes WebUI Rewrite"
status: completed
created: 2026-06-27
source: brainstorm
brainstorm: ../reports/brainstorm-260627-0330-nothingos-webui-rewrite-report.md
blockedBy: []
blocks: []
---

# NothingOS-inspired Hermes WebUI Rewrite

Rewrite toàn bộ Hermes WebUI thành 1 design system NothingOS-inspired (dark monochrome, dot-matrix, widget-first, ambient status), pixel-perfect shell chính theo `ref/nothingos-webui-reference.html`. Nền tảng: **v1 vanilla `static/`** (có source + đã nối API). Xoá v2 `frontend/dist`.

## Strategy: Cách C Hybrid

Giữ nguyên mọi `id` JS (không vỡ logic 56k dòng). Tái cấu trúc layout grid theo reference. Rewrite design system. Gỡ 14 skin + picker, chỉ còn `nothingos`.

## Acceptance Criteria (toàn plan)

1. Shell chính pixel-perfect reference: ambient strip (top) + OS rail + agent surface + glance widgets (phải) + quick command tray (bottom).
2. Chỉ 1 skin `nothingos`; settings KHÔNG còn skin/theme picker.
3. Reload với `localStorage['hermes-skin']='sienna'` / theme cũ → vẫn render NothingOS.
4. Login / session list / chat stream / composer submit / tool-call states chạy như cũ.
5. Console errors = 0; body text contrast đạt; mobile 390px không overflow.
6. Không còn `frontend/dist`; route `/` serve v1 static; không patch minified JS.

## Phases

| # | Phase | Priority | Depends | File | Status |
|---|---|---|---|---|---|
| 1 | Route switch + dọn v2 | P1 | — | phase-01-route-switch-remove-v2.md | ✅ done |
| 2 | Gỡ theme/skin system → single skin | P1 | 1 | phase-02-remove-theme-system.md | ✅ done |
| 3 | Design tokens | P1 | 2 | phase-03-design-tokens.md | ✅ done |
| 4 | Tái cấu trúc shell (layout) | P1 | 3 | phase-04-restructure-shell.md | ✅ done |
| 5 | 3 thành phần mới + JS feed | P2 | 4 | phase-05-new-components.md | ✅ done |
| 6 | Rewrite component styling + màn phụ | P2 | 4 | phase-06-component-styling.md | ✅ done |
| 7 | QA gates | P1 | 5,6 | phase-07-qa-gates.md | ✅ done |

**Implementation note (Session 2026-06-27):** Phase 4 shell mapping resolved per Sếp's decision —
giữ chức năng tối thượng, bọc khung OS (ambient + quick tray) quanh 4-region flex layout, không
pixel-perfect. Workspace rightpanel giữ nguyên; glance widgets chèn vào đó. Phase 1 cũng re-enable
v1 `/login` block (vì `/login` cũ serve v2 shell, đã xoá cùng frontend_v2). QA dùng Orca embedded
browser (headless Chrome không snapshot được app live-poll). Mobile 390px pixel-shot còn pending —
xem qa report.

## Scope boundaries

- **OUT:** không sửa backend API logic; không thêm feature; không dựng React/Vite.
- **Pixel-perfect chỉ shell chính.** Màn phụ (settings/onboarding/terminal/kanban/workspace) áp chung design system, không pixel-match (không có ảnh mẫu).

## Key risks

- `style.css` 5.335 dòng đan 15 skin → gỡ cẩn thận theo selector `[data-skin]`, giữ base.
- JS bám `id` → chỉ bọc wrapper / đổi class, KHÔNG đổi/xoá id.
- Route `/` hiện redirect `/v2/` ("v1 shell retired" `routes.py:4724`) → phải đảo lại + kiểm tra deep-link `/session/<id>`.

## Open questions

- None — đã giải quyết ở Validation Session 1.

## Validation Log

### Session 1 (2026-06-27)

**Verification Results (Full tier, 7 phases):**
- Claims checked: 6 · Verified: 6 · Failed: 0 · Unverified: 0
- ✅ `routes.py:4732` có block `if False:` "legacy v1 shell (disabled)" — serve `static/index.html` + inject CSRF/upload/version. `index.html:31` còn placeholder `__CSRF_TOKEN_JSON__`. → Phase 1 re-enable block này.
- ✅ `_pickTheme`/`_pickSkin` ở `boot.js:1593/1609`. `_SKINS` 16 entry, fallback `nothing` (`boot.js:1489`).
- ✅ Deep-link `/session/<id>` v1 handle được (`boot.js:1954`) — CSRF login-loop risk đã khử.

**Decisions confirmed:**
1. Phase 1 route: **re-enable block `if False:` có sẵn** (routes.py:4732) thay vì viết route mới.
2. Xoá v2: **xoá `frontend/dist` + `frontend_v2.py` ngay trong Phase 1** (không tách commit rollback).
3. QA Phase 7: **Claude tự chạy `bootstrap.py` local + curl health + screenshot** desktop/mobile.
4. Thứ tự: **tuần tự 1→7**, mỗi phase verify xong mới sang phase sau.

**Recommendation:** proceed — 0 failed, plan eligible for implementation.

### Whole-Plan Consistency Sweep
- Re-read plan.md + 7 phase files. Propagated: Phase 1 (re-enable block + xoá v2 ngay), Phase 7 (QA tự chạy server).
- Stale check: "commit riêng/tách commit/rollback nhanh" → đã reconcile (xoá v2 cùng commit). Open questions → None. `frontend_v2`/`dist` refs nhất quán across files.
- **0 unresolved contradictions.**
