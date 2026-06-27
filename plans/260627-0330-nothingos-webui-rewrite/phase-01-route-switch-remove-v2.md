---
phase: 1
title: "Route switch + dọn v2"
status: completed
priority: P1
dependencies: []
---

# Phase 1: Route switch + dọn v2

## Overview
Đảo route `/` (và deep-link `/session/<id>`) từ serve v2 SPA về serve v1 `static/index.html`. Gỡ nhánh `/v2/` và file phục vụ v2. Bước nền: mọi phase sau sửa UI ở static mới có tác dụng.

## Requirements
- Functional: `/`, `/index.html`, `/session/<id>` → serve `static/index.html` (qua client router static). `/login` giữ nguyên. Auth/CSRF không đổi hành vi.
- Non-functional: không phá deep-link; không patch minified.

## Architecture
**[Validated S1]** Route hiện tại (`api/routes.py:4724`): `/` + `/session/` → 302 redirect `/v2/` hoặc `/login`. v1 static handle `/session/<id>` (xác nhận `boot.js:1954`).

**Phát hiện then chốt:** `routes.py:4732` có sẵn block `if False:  # legacy v1 shell (disabled, kept for reference)` — đã serve `static/index.html` (`_INDEX_HTML_PATH`) + replace `__WEBUI_VERSION__`/`__MAX_UPLOAD_BYTES__`/`__CSRF_TOKEN_JSON__` + `inject_extension_tags`. `index.html:31` còn nguyên placeholder. → **Re-enable block này**, không viết serve mới.

## Related Code Files
- Modify: `api/routes.py` (~4724 nhánh redirect `/`+`/session/`; ~4732 block `if False:` re-enable; ~5029 nhánh `/v2/` xoá)
- Delete (ngay trong phase này): `api/frontend_v2.py`, `frontend/dist/` (toàn bộ)
- Reference: placeholder ở `static/index.html:29-31` (`__CSRF_TOKEN_JSON__` etc.)

## Implementation Steps
1. Sửa nhánh redirect (`routes.py:4724`): khi logged-in → KHÔNG redirect `/v2/`, mà fall through vào block serve v1 shell (logged-out vẫn → `/login`).
2. Đổi `if False:` (4732) → điều kiện thật (serve khi `/`, `/index.html`, `/session/...`). Giữ inject CSRF/upload/version + `inject_extension_tags` y nguyên.
3. Xoá nhánh `if parsed.path == "/v2"...` (routes.py:5029) + import `frontend_v2`.
4. Xoá `api/frontend_v2.py` + `frontend/dist/` (toàn bộ) ngay trong phase này.
5. Cập nhật `.gitignore` nếu có entry trỏ dist.

## Success Criteria
- [ ] `curl /` (authed) trả `static/index.html`, không 302 `/v2/`.
- [ ] `__CSRF_TOKEN_JSON__` được replace bằng token thật (không còn placeholder trong HTML trả về).
- [ ] `/session/<id>` reload load đúng session.
- [ ] Login flow + CSRF không đổi hành vi.
- [ ] `frontend/dist` + `api/frontend_v2.py` đã xoá; `rg "/v2"` không còn route sống.
- [ ] Console 0 lỗi sau switch.

## Risk Assessment
- **Risk [đã khử S1]:** CSRF inject — block `if False:` có sẵn đã làm đầy đủ; chỉ cần re-enable.
- **Risk:** deep-link `/session/<id>` vỡ. **Mitigation:** `boot.js:1954` cho thấy v1 handle; test thủ công.
- **Rollback:** xoá v2 cùng commit (quyết định S1) → rollback bằng `git revert` cả commit, không tách. Chấp nhận đánh đổi gọn hơn rollback nhanh.
