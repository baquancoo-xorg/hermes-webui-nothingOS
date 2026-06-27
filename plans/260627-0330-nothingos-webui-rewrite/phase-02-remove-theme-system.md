---
phase: 2
title: "Gỡ theme/skin system → single skin"
status: completed
priority: P1
dependencies: [1]
---

# Phase 2: Gỡ theme/skin system → single skin

## Overview
Gỡ 15 skins + theme (light/dark/system) về duy nhất `nothingos`. Bỏ skin/theme picker khỏi settings. Migration guard: localStorage cũ không thoát khỏi NothingOS. Thoả P0 spec mục 3.1.

## Requirements
- Functional: app luôn render `data-skin="nothingos"` (đổi tên từ `nothing`), dark-only. Settings không lộ picker. localStorage `hermes-skin/hermes-theme` cũ → ép `nothingos`.
- Non-functional: không vỡ logic settings khác (font-size, language giữ nguyên nếu muốn).

## Architecture
- `boot.js:1489` `_SKINS` (15 skin) → rút còn 1 `nothingos`. `_VALID_SKINS` tự co theo.
- `boot.js:1519 _normalizeAppearance` → luôn trả `{theme:'dark', skin:'nothingos'}` bất kể input.
- `boot.js:1568 _applyTheme` / `1586 _applySkin` → ép root `data-skin="nothingos"`, dark.
- `boot.js:1770-1795` reconcile localStorage↔server → đơn giản hoá: luôn set `nothingos`.
- `index.html:1023-1123` settings pane Appearance: gỡ block Theme (1031-1052) + Skin picker (1055-1122). Giữ phần khác (font-size) nếu có.
- `style.css`: xoá 14 block `[data-skin="..."]` (ares/catppuccin/charizard/geist-contrast/graphite/hepburn/mono/neon/nous/poseidon/sienna/sisyphus/slate/zeus). Giữ base + `nothing`→ rename `nothingos`.

## Related Code Files
- Modify: `static/boot.js` (1489, 1519, 1568, 1586, 1770-1795)
- Modify: `static/index.html` (1023-1123 appearance pane)
- Modify: `static/style.css` (xoá block 14 skin; rename `nothing`→`nothingos`)
- Modify: `static/ui.js` (nếu có handler `_pickTheme`/`_pickSkin` → vô hiệu/gỡ)

## Implementation Steps
1. `boot.js`: `_SKINS = [{value:'nothingos', name:'NothingOS'}]`. `_normalizeAppearance` luôn return nothingos/dark. `_applySkin('nothingos')` hardcode. Reconcile block: drop, chỉ `_applyTheme('dark'); _applySkin('nothingos')`.
2. Migration guard: ở boot, `localStorage.setItem('hermes-skin','nothingos'); localStorage.setItem('hermes-theme','dark')` (ghi đè giá trị cũ).
3. `index.html`: xoá DOM Theme picker + Skin picker trong `#settingsPaneAppearance`. Giữ hidden input nếu JS đọc, set value cố định.
4. `style.css`: grep `[data-skin=` → xoá 14 block, rename `nothing`→`nothingos`. Giữ base/`:root`.
5. Xoá CSS overlay anti-pattern từ commit ace6b5b (pill 999px, neon glow) — sẽ thay ở Phase 3/6.

## Success Criteria
- [ ] `localStorage.setItem('hermes-skin','sienna'); reload` → vẫn NothingOS.
- [ ] Settings → Appearance: không còn nút chọn skin/theme.
- [ ] `rg 'data-skin=\"(ares|sienna|neon|...)\"' static/style.css` → 0 kết quả.
- [ ] Root luôn `data-skin="nothingos"`.
- [ ] Font-size/language settings vẫn hoạt động (nếu giữ).

## Risk Assessment
- **Risk:** xoá nhầm base CSS khi cắt skin block. **Mitigation:** chỉ xoá selector có `[data-skin="X"]` prefix; diff review.
- **Risk:** JS khác đọc `_SKINS` để render list. **Mitigation:** grep `_SKINS` usage trước khi cắt.
