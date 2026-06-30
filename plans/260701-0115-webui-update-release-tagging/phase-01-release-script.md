---
phase: 1
title: "scripts/release.sh — cut + push annotated tag"
status: completed
priority: P1
dependencies: []
---

# Phase 1: scripts/release.sh

## Overview
Add a single release script that turns the current `main` HEAD into a published release tag
`vX.Y.Z-nothingos`, pushes it, and optionally creates a GitHub Release. This is the only thing the
fork was missing for the in-app update banner to fire.

## Requirements
- Functional: `scripts/release.sh <version>` → validate → create annotated tag → push tag → optional `gh release create`.
- Non-functional: pure bash, no new deps; safe-by-default (refuses unsafe states); idempotent-safe (won't silently clobber an existing tag).

## Architecture
- Tag scheme: `v<version>-nothingos` where `<version>` matches `^\d+\.\d+\.\d+$` (semver). Final tag regex: `^v\d+\.\d+\.\d+-nothingos$`. Verified compatible with the updater's `git tag --list 'v*' --sort=-v:refname`.
- Version stamp: `api/config.py:_detect_webui_version()` uses `git describe --tags` → a new tag automatically advances `WEBUI_VERSION`. No code change needed.
- Preconditions enforced (fail fast with clear message):
  1. Run from repo root, inside a git work tree.
  2. Current branch is `main` (override with `--allow-branch` for hotfix tags).
  3. Working tree clean (`git status --porcelain` empty).
  4. Local `main` == `origin/main` (fetched; not ahead/behind) so the tag points at the pushed HEAD.
  5. Version arg present + matches semver; resulting tag does not already exist locally or on origin.
- Steps performed:
  1. `git fetch origin --tags --quiet`.
  2. Create annotated tag: `git tag -a "v<ver>-nothingos" -m "Release v<ver>-nothingos"`.
  3. `git push origin "v<ver>-nothingos"`.
  4. If `gh` present and `--gh-release` passed: `gh release create "v<ver>-nothingos" --title ... --generate-notes` (auto changelog from commits). Skip gracefully if `gh` missing.
- Flags: `--gh-release` (also create GitHub Release), `--allow-branch` (permit tagging a non-main branch), `--dry-run` (print actions, mutate nothing).

## Related Code Files
- Create: `scripts/release.sh` (chmod +x).
- Reference only (do NOT modify): `api/config.py` (`_detect_webui_version`), `api/updates.py` (`_release_tags`).

## Implementation Steps
1. Write `scripts/release.sh` with `set -euo pipefail`, usage/help, arg + flag parsing.
2. Implement the 5 precondition checks; each prints a one-line actionable error and exits non-zero.
3. Implement tag create + push; on `--dry-run`, echo the exact git commands instead of running them.
4. Implement optional `gh release create` guarded by `command -v gh` and `--gh-release`.
5. Make executable; smoke-test `--dry-run` and a bad-version arg locally (no real tag pushed).

## Success Criteria
- [ ] `scripts/release.sh 1.1.0 --dry-run` prints the tag+push it WOULD run, mutates nothing.
- [ ] Bad inputs rejected: missing version, `1.1`, `v1.1.0`, dirty tree, non-main branch (without `--allow-branch`), main out of sync with origin, pre-existing tag.
- [ ] Real run creates `v<ver>-nothingos` annotated tag on origin; `git describe --tags` reflects it.
- [ ] `--gh-release` creates a GitHub Release with generated notes when `gh` is available; absence of `gh` is a graceful skip, not an error.

## Risk Assessment
- **Tagging the wrong commit** → precondition 4 (main == origin/main) + clean tree guarantee tag points at the pushed HEAD.
- **Malformed tag breaks semver-sort** → strict regex validation before tagging.
- **Accidental clobber of existing release** → refuse if tag already exists locally or on origin (no `-f`).
- **`gh` not authenticated** → wrap in `command -v gh` + non-fatal warning; tag/push still succeed.
