---
phase: 3
title: "Document the release + update flow"
status: completed
priority: P2
dependencies: [1, 2]
---

# Phase 3: Document the release + update flow

## Overview
Write down how to cut a release and how the in-app update works, so the missing-tag trap never
recurs. Captures the Docker caveat explicitly.

## Requirements
- Functional: a maintainer can cut a release from docs alone; a user understands when/why the banner appears and what "Update Now" does.
- Non-functional: concise; live next to existing deploy docs; no duplication of the update engine internals.

## Architecture
- Add a **"Releasing & Updates"** section to `docs/nothingos-deploy.md` (already covers deploy/switch/rollback — natural home). Cover:
  1. **Cut a release:** `scripts/release.sh X.Y.Z [--gh-release]` → what it validates, what it pushes.
  2. **How the banner decides:** compares against latest `v*-nothingos` release tag; tag-pinned installs follow stable releases, `main`-tracking clones follow per-commit (engine handles both automatically).
  3. **What "Update Now" does:** `git fetch` + `git pull --ff-only` to the target ref, then server restart; local edits are stashed/restored; diverged history fails safe and shows **Force update**.
  4. **Docker caveat (important):** for installs running a built Docker *image*, "Update Now" runs `git pull` inside the container and does NOT persist across restart (immutable image). Those users update via `docker pull` / rebuild instead. The updater has no Docker-awareness for the webui repo.
- README: add a short **"Updating"** subsection (or one line under install) pointing to the deploy doc, so users discover the banner exists.

## Related Code Files
- Modify: `docs/nothingos-deploy.md` (append "Releasing & Updates").
- Modify: `README.md` (short "Updating" pointer).
- Reference only: `scripts/release.sh` (phase 1), `api/updates.py` (behavior described, not changed).

## Implementation Steps
1. Append "Releasing & Updates" to `docs/nothingos-deploy.md` with the 4 subsections above; include the exact `release.sh` invocation.
2. Add a brief "Updating" pointer in `README.md` (near install / theme-toggle section).
3. Verify all commands in docs are copy-paste correct against the phase-1 script's real flags.
4. Proofread: dates, links, tag format consistent with `scripts/release.sh`.

## Success Criteria
- [ ] `docs/nothingos-deploy.md` has a "Releasing & Updates" section a maintainer can follow unaided.
- [ ] Docker caveat is stated explicitly.
- [ ] README points users to the update mechanism.
- [ ] Every command in the docs matches `scripts/release.sh`'s actual interface.

## Risk Assessment
- **Docs drift from script flags** → write docs after phase 1 is final; cross-check flags.
- **Users on Docker expect Update Now to work** → explicit caveat prevents confusion + support load.
