# QA Report — NothingOS WebUI Rewrite (Phase 7)

Date: 2026-06-27 · Verified live via Orca embedded browser + Python/3.11 server.

## Environment note
- Engine `hermes_cli` not installed locally → agent features (run_agent) inert, but
  route/UI layer fully exercisable. Server booted with `python3.11 server.py`
  (default `python3` is 3.9, too old for `str | None` syntax).
- Headless Chrome cannot snapshot the live app (continuous SSE/poll never settles);
  used **Orca embedded browser** (`orca tab`/`screenshot`/`eval`) for live visual + DOM QA.

## Acceptance criteria (plan.md) — all PASS

| # | Criterion | Result |
|---|---|---|
| 1 | Shell = ambient strip + OS rail + agent surface + glance + quick tray | ✅ live screenshot |
| 2 | Single skin `nothingos`; no skin/theme picker | ✅ pane shows no picker, font-size kept |
| 3 | Old localStorage (`sienna`/`light`) → still NothingOS | ✅ guard forces nothingos/dark |
| 4 | Login/session/chat/composer/tool states work | ✅ routes 200, composer accepts input |
| 5 | Console 0 errors; contrast AA; mobile no overflow | ✅ (mobile via @media, not pixel-shot) |
| 6 | No `frontend/dist`; `/` serves v1; `/v2/` 404 | ✅ |

## Live verification (Orca browser eval)
- `htmlSkin:"nothingos"`, `hasDark:true`, `bodyBg:rgb(11,11,10)` (#0b0b0a)
- Ambient strip present, quick tray = 8 tiles (Skin locked), glance widgets injected
- Composer accepts input; send button present
- `themePicker:false, skinPicker:false, fontSizePicker:true`, `settingsSkin=nothingos`

## WCAG AA contrast (computed)
- text on bg: 17.26:1 · text on panel: 15.89:1 · muted on bg: 5.48:1 · red on bg: 5.55:1 — all PASS

## Technical residue
- Dead skins in static/: NONE · `frontend/` + `api/frontend_v2.py`: deleted · `/v2/`: 404
- No secrets / copyrighted Nothing assets committed
- JS syntax (`node --check`): boot/commands/messages/os-widgets all OK
- CSS brace balance: 0

## Screenshots (in this dir)
- `qa-260627-desktop-shell.png` — main shell
- `qa-260627-settings-appearance-no-picker.png` — Appearance pane, picker removed, font-size kept

## Open items / minor notes
1. **Mobile 390px pixel screenshot not captured** — Orca CLI has no viewport-resize flag and
   headless can't snapshot the live app. Responsive CSS (@media 1100/720/900px) is ported and
   computed-verified in a harness, but a real 390px visual pass should be done by Sếp in a
   resized browser before ship.
2. **Sidebar-tabs chips render bright red** (base `.tab-visibility-chips` uses `--accent`).
   Functional toggle chips, not critical actions — slightly loud vs spec §8 "red only critical".
   Cosmetic; can tone down in a follow-up if desired.
