---
phase: 2
title: "End-to-end verification of the update banner"
status: completed
priority: P1
dependencies: [1]
---

# Phase 2: Verify the update banner end-to-end

## Overview
Prove the loop works: with a new tag published, a client on an older version sees the banner and
"Update Now" actually advances the checkout. No product code changes — this is a verification gate
that captures evidence.

## Requirements
- Functional: confirm banner appears for a behind client; confirm apply pulls forward + restarts; confirm version stamp advances.
- Non-functional: use existing test affordances (`?test_updates=1`, `?simulate=1`); do not add test-only code paths.

## Architecture
- Two verification tracks:
  - **Track A — simulate (fast, no real tag):** open `/?test_updates=1` → banner is force-shown (boot.js bypasses sessionStorage guards). Confirms the UI renders + buttons wire up. Confirms nothing about real git state.
  - **Track B — real tag (true end-to-end):** cut a throwaway tag with `release.sh` at HEAD; in a second clone checked out to the OLD tag, start the server and confirm `/api/updates/check` reports `behind > 0` and the banner shows; click **Update Now**; confirm `git pull --ff-only` advances to the new tag, server restarts, banner clears.
- Endpoints exercised: `POST /api/updates/check`, `POST /api/updates/apply` (already implemented).
- The throwaway tag is deleted after the test (`git push origin :refs/tags/<tag>` + local delete) so it doesn't pollute the real release history — OR use a real intended release if cutting one anyway.

## Related Code Files
- Reference only (no edits): `static/boot.js` (auto-check), `static/ui.js` (banner show/apply), `api/routes.py` (`/api/updates/*`), `api/updates.py`.
- Evidence: save screenshots to `plans/260701-0115-webui-update-release-tagging/reports/`.

## Implementation Steps
1. **Track A:** start server; open `http://127.0.0.1:8787/?test_updates=1`; screenshot the banner; click through "Later" + confirm dismiss.
2. **Track B setup:** ensure HEAD is at a clean pushed `main`; run `scripts/release.sh <next> --dry-run` then for real (or a throwaway `vX.Y.Z-nothingos`).
3. **Track B behind-client:** in a separate clone, `git checkout <older-tag>`; start it on a different port (`HERMES_WEBUI_PORT`); confirm `/api/updates/check` → `behind > 0` and banner renders.
4. **Track B apply:** click **Update Now**; confirm pull-forward to the new tag, auto-restart, banner clears, `git describe --tags` advanced. Screenshot before/after.
5. If a throwaway tag was used, delete it locally + on origin.
6. Record results (pass/fail per track) in the plan's reports dir.

## Success Criteria
- [ ] Track A: banner force-shows under `?test_updates=1`; Later dismisses it.
- [ ] Track B: behind client reports `behind > 0` and shows the banner with real data.
- [ ] Track B: **Update Now** advances the checkout to the new tag and restarts; banner clears; version stamp updated.
- [ ] Throwaway tag (if any) removed from origin; real release history clean.
- [ ] Evidence screenshots saved under the plan's `reports/`.

## Risk Assessment
- **Polluting release history with test tags** → use `--dry-run` first; delete throwaway tags; or fold the test into a real intended release.
- **Apply fails on diverged local clone** → expected when the test clone has local commits; use a pristine checkout; the Force-update path is out of scope to fix (already exists).
- **Port/state collision with the dev server** → run the behind-client on a separate `HERMES_WEBUI_PORT` + `HERMES_WEBUI_STATE_DIR`.
