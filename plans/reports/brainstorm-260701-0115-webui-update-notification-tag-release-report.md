---
title: "WebUI Update Notification — root cause & tag-release fix"
type: brainstorm-report
date: 2026-07-01
status: agreed
topic: "Thông báo + nút update trên WebUI khi repo có bản mới"
repo: baquancoo-xorg/hermes-webui-nothingOS
modes: []
---

# WebUI Update Notification — Brainstorm Report

## TL;DR (đảo ngược giả định ban đầu)

Sếp nghĩ: *"chưa có tính năng thông báo/update, muốn update phải cài lại từ repo."*

**Thực tế (đã verify bằng đọc code + test):** tính năng update **đã tồn tại đầy đủ và hoạt động** trong fork. Nó "im lặng" vì **fork chưa cắt git tag mới** — updater so sánh theo *release tag*, mà fork mới chỉ có 1 tag cũ (`v1.0.0-nothingos`) trong khi `main` đã đi xa 9 commit.

→ Đây là **vấn đề quy trình phát hành**, không phải thiếu tính năng UI. Giải pháp = quy trình cắt tag + verify, **gần như 0 dòng code sản phẩm**.

---

## Problem statement

- Người dùng cài WebUI fork (`baquancoo-xorg/hermes-webui-nothingOS`) không thấy thông báo khi repo có commit mới → tưởng phải clone lại để cập nhật.
- Mong muốn: WebUI hiện thông báo + nút "Update" khi có bản mới.

## Hiện trạng đã có sẵn (evidence)

| Thành phần | Vị trí | Trạng thái |
|---|---|---|
| Backend check/apply/force/summary | `api/updates.py` (1579 dòng) | ✅ Đầy đủ |
| Endpoints | `/api/updates/{check,apply,force,summary}` (`api/routes.py`) | ✅ |
| Update banner UI | `static/index.html:425` (`#updateBanner`) | ✅ Có nút **Update Now / Later / Force update** |
| Auto-check khi mở app | `static/boot.js:2247` (1 lần/tab session) | ✅ |
| Show banner + apply | `static/ui.js:7696+`, `static/panels.js:9677` (check thủ công trong Settings) | ✅ |
| LLM "what's new" summary | `api/updates.py:1014` | ✅ |
| Cờ test bypass | `?test_updates=1` (force banner), `?simulate=1` (fake data) | ✅ Có sẵn để verify |

Updater tự `git fetch origin` (chính là fork của Sếp) — **không hardcode về repo gốc** nesquena.

## Root cause (đã verify)

Updater check theo **release tag**, không theo commit branch:

- `_release_tags()` = `git tag --list 'v*' --sort=-v:refname` (newest-first).
- `_release_gap()` đếm số tag giữa tag-hiện-tại và tag-mới-nhất.
- Fork chỉ có **1 tag** `v1.0.0-nothingos` (ở commit `2b16af7`); `main` HEAD giờ = `v1.0.0-nothingos-9-gc6fd5d2` (9 commit sau, chưa tag).
- → `_release_gap` = 0 → **banner không hiện**.

**Test xác nhận tag scheme tương thích:** `git --sort=-v:refname` xếp đúng `v2.0.0 > v1.10.0 > v1.2.0 > v1.1.0 > v1.0.0` *kể cả* có suffix `-nothingos`. Nên tag `vX.Y.Z-nothingos` chạy được ngay, không cần đổi scheme.

## Nuance quan trọng: 2 nhóm người dùng (code đã xử lý cả hai)

| Nhóm | HEAD | Hành vi updater |
|---|---|---|
| **A — cài đúng tag** (`git checkout v1.0.0-nothingos`) | đúng trên tag | So theo tag → tag mới = banner hiện. Theo **release ổn định**. |
| **B — clone `main` thường** | đã vượt tag (`...-9-g...`) | `_head_is_past_latest_tag`=true → rẽ sang so `origin/main` → đếm commit thật. Theo **mỗi commit push lên main**. |

→ Hướng "theo tag" Sếp chọn **đã tự động bao hàm** hành vi theo-commit cho nhóm B. Không cần code thêm cho 2 chế độ.

---

## Approaches đã cân nhắc

### A. Theo tag (CHỌN) — đúng thiết kế sẵn
- **Việc làm:** mỗi release tạo + push annotated tag `vX.Y.Z-nothingos`.
- **Ưu:** ~0 code sản phẩm; đúng ý đồ gốc; người cài-tag thấy release ổn định, người track-main thấy theo commit; semver-sort đã verify ổn.
- **Nhược:** phải nhớ cắt tag mỗi lần phát hành (chính cái bẫy vừa rồi) → mitigate bằng `release.sh` + docs.

### B. Theo commit main (loại)
- Sửa updater bỏ tag, luôn so `origin/main`.
- **Nhược:** sửa logic backend đã ổn định (rủi ro regression); spam banner mỗi commit nhỏ; **không cần** vì nhóm B đã có hành vi này sẵn.

### C. Cả hai có toggle (loại)
- Over-engineer cho 1 maintainer; YAGNI.

## Giải pháp chốt: A — quy trình tag + verify + docs

**Phạm vi (sau khi em verify apply path + Docker): KHÔNG sửa code update.** Apply path (`api/updates.py:1345+`) đã chắc: stash local → `pull --ff-only` → restore stash, xử lý đủ conflict/diverged/untracked; diverge thì fail an toàn + lộ nút **Force update**. Không cần đụng.

### Hạng mục triển khai (cho /ck:plan)

1. **`scripts/release.sh`** (mới): nhận version → tạo annotated tag `vX.Y.Z-nothingos` ở HEAD main → push tag → (optional) tạo GitHub Release qua `gh`. Validate định dạng tag + main clean + đã push commit.
2. **Verify end-to-end (1 lần):**
   - Cắt 1 tag thử (vd `v1.1.0-nothingos`) ở HEAD hiện tại, push.
   - Giả lập client cũ: `git checkout v1.0.0-nothingos` ở 1 clone khác (hoặc dùng `?test_updates=1` để force banner) → xác nhận banner hiện, "Update Now" chạy `git pull --ff-only` về tag mới, server restart, banner tắt.
3. **Docs** (`docs/` + bổ sung README "Updating"): ghi rõ
   - quy trình cắt release (chạy `release.sh`),
   - 2 nhóm người dùng (tag vs main) hành xử ra sao,
   - **cảnh báo Docker:** "Update Now" chạy `git pull` *trong container* — với bản chạy bằng Docker image bất biến, update không persist sau restart; người Docker phải `docker pull` image mới / rebuild. (Updater không nhận biết Docker cho webui — ngoài scope lần này.)

### Out of scope (lần này)
- Sửa logic `api/updates.py` (đã hoạt động đúng).
- Hỗ trợ update cho Docker-image deployment (cần cơ chế khác; chỉ ghi cảnh báo).
- Đổi nhãn/thương hiệu banner sang NothingOS (cosmetic; có thể làm sau nếu Sếp muốn).
- GitHub Actions tự cắt tag (chỉ làm nếu sau này release thường xuyên).

## Acceptance criteria

- Chạy `scripts/release.sh X.Y.Z` → tag `vX.Y.Z-nothingos` xuất hiện trên origin.
- Client đang ở tag cũ mở WebUI → banner "update available" hiện trong vài giây, kèm nút Update Now.
- Bấm Update Now → repo `pull --ff-only` lên tag mới, server tự restart, banner biến mất, version stamp đổi.
- `?test_updates=1` vẫn buộc banner hiện để demo.
- Docs mô tả quy trình release + cảnh báo Docker.

## Risks & mitigations

| Risk | Mức | Mitigation |
|---|---|---|
| Quên cắt tag (bẫy vừa rồi tái diễn) | Cao | `release.sh` + mục Docs "cách phát hành"; cân nhắc GH Action sau |
| Người track-main có commit local → `pull --ff-only` fail | Trung | Đúng hành vi an toàn; nút **Force update** đã có; ghi docs |
| Người chạy Docker image bấm Update → không persist | Trung | Docs cảnh báo; Docker-update ngoài scope |
| Tag scheme sai định dạng phá semver-sort | Thấp | `release.sh` validate regex `^v\d+\.\d+\.\d+-nothingos$` |

## Next steps

1. `/ck:plan` cho hạng mục: `release.sh` + verify + docs.
2. Sau plan: implement script → cắt tag thật đầu tiên → verify banner.

## Unresolved questions

- Sếp có muốn `release.sh` tạo luôn **GitHub Release** (changelog) qua `gh` không, hay chỉ tag thuần? (mặc định em đề xuất: tag + optional GH release flag).
- Có cần đổi nhãn banner sang thương hiệu NothingOS ngay đợt này không, hay để sau? (mặc định: để sau — cosmetic).
