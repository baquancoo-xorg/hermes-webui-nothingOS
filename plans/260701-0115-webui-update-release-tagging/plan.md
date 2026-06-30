---
title: "WebUI Update Notifications — Release Tagging Process"
status: completed
created: 2026-07-01
scope: project
blockedBy: []
blocks: []
source: brainstorm
brainstorm: ../reports/brainstorm-260701-0115-webui-update-notification-tag-release-report.md
---

# WebUI Update Notifications — Release Tagging Process

> Make the **already-built** in-app update banner fire for the fork by establishing a
> release-tagging process. No update-engine code changes — `api/updates.py` already
> works; it stays silent only because the fork never cuts new git tags.

## Why this plan exists

The update feature is complete (`api/updates.py` check/apply/force/summary + `#updateBanner` +
boot.js auto-check + ui.js apply). It compares against **release tags**. The fork has one stale
tag (`v1.0.0-nothingos`) while `main` is 9 commits ahead → `_release_gap == 0` → banner never
shows. Root cause = **missing release process**, not missing feature.

Verified: `git tag --sort=-v:refname` orders `vX.Y.Z-nothingos` correctly (suffix-safe). The
apply path stashes local changes → `pull --ff-only` → restores; diverged history fails safely and
exposes the existing **Force update** button. Two user groups are already handled by the engine:
tag-pinned installs follow stable releases; `main`-tracking clones follow per-commit.

## Hard constraints

- **Do NOT modify `api/updates.py`** update/check/apply logic. It is correct and battle-tested.
- Tag scheme MUST stay `vX.Y.Z-nothingos` (matches `v*` filter + semver-sort; verified).
- `release.sh` must refuse to tag a dirty/un-pushed/non-main HEAD or a malformed version.
- Docs only add a "Releasing & Updates" section; do not rewrite existing deploy docs.
- No secrets in script or docs.

## Phases

| # | Phase | Status | Priority | Depends |
|---|-------|--------|----------|---------|
| 1 | `scripts/release.sh` — cut + push annotated tag (optional GH Release) | completed | P1 | — |
| 2 | End-to-end verification of the update banner | completed | P1 | 1 |
| 3 | Document the release + update flow (incl. Docker caveat) | completed | P2 | 1,2 |

## Acceptance (whole plan)

- `scripts/release.sh 1.1.0` creates + pushes annotated tag `v1.1.0-nothingos` on origin; refuses dirty/non-main/bad-version.
- A client on an older tag (or `?test_updates=1`) shows the update banner within seconds; **Update Now** runs `git pull --ff-only`, server restarts, banner clears, version stamp advances.
- Docs describe: how to cut a release, how tag vs main users behave, and the Docker-image caveat (git pull inside an immutable image does not persist).
- No change to `api/updates.py`; `npm run lint:runtime` + `node --check` unaffected (no JS touched).

## Out of scope

- Update support for Docker-image deployments (documented caveat only).
- Rebranding the banner copy to NothingOS (cosmetic; later).
- GitHub Actions auto-tagging (revisit if releases become frequent).
- Changing the update engine's tag-vs-branch comparison logic.

## Phase files

- [phase-01-release-script.md](phase-01-release-script.md)
- [phase-02-verify-update-banner.md](phase-02-verify-update-banner.md)
- [phase-03-document-release-update-flow.md](phase-03-document-release-update-flow.md)
