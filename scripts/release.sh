#!/usr/bin/env bash
set -euo pipefail

# release.sh — cut and push a NothingOS WebUI release tag.
#
# The in-app update banner (api/updates.py) compares the running checkout against
# the latest published release tag. The fork stays "up to date" forever unless a
# new tag is pushed, so cutting a release == pushing a `vX.Y.Z-nothingos` tag.
#
# Usage:
#   scripts/release.sh <X.Y.Z> [--gh-release] [--allow-branch] [--dry-run]
#
#   <X.Y.Z>          Semantic version (digits only), e.g. 1.1.0. The pushed tag
#                    is `vX.Y.Z-nothingos`.
#   --gh-release     Also create a GitHub Release with auto-generated notes
#                    (requires `gh`; skipped with a warning if unavailable).
#   --allow-branch   Permit tagging a branch other than `main` (e.g. a hotfix).
#   --dry-run        Print the git commands that WOULD run; mutate nothing.
#
# Exit non-zero with a one-line reason on any precondition failure.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VERSION=""
GH_RELEASE=0
ALLOW_BRANCH=0
DRY_RUN=0

usage() {
  sed -n '3,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

die() {
  echo "release: $1" >&2
  exit 1
}

# ── Parse args ───────────────────────────────────────────────────────────────
for arg in "$@"; do
  case "$arg" in
    --gh-release)   GH_RELEASE=1 ;;
    --allow-branch) ALLOW_BRANCH=1 ;;
    --dry-run)      DRY_RUN=1 ;;
    -h|--help)      usage; exit 0 ;;
    -*)             die "unknown flag: $arg (see --help)" ;;
    *)
      [ -z "$VERSION" ] || die "unexpected extra argument: $arg"
      VERSION="$arg"
      ;;
  esac
done

[ -n "$VERSION" ] || { usage; die "missing <X.Y.Z> version argument"; }

# ── Validate version + derive tag ────────────────────────────────────────────
# Digits-only semver; the updater sorts tags with `git --sort=-v:refname`, which
# orders the `-nothingos` suffix correctly as long as the numeric core is semver.
if ! printf '%s' "$VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  die "version must be X.Y.Z digits only (got: '$VERSION')"
fi
TAG="v${VERSION}-nothingos"

# ── Preconditions ────────────────────────────────────────────────────────────
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git work tree"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$BRANCH" != "main" ] && [ "$ALLOW_BRANCH" -eq 0 ]; then
  die "current branch is '$BRANCH', not 'main' (use --allow-branch to override)"
fi

# Only tracked-file changes matter — untracked scratch files (logs, local notes)
# never enter the tag, which points at committed HEAD.
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  die "tracked files have uncommitted changes; commit or stash before releasing"
fi

# Tag must point at the pushed HEAD, so local must equal origin for this branch.
git fetch origin --tags --quiet || die "git fetch origin failed; check network/remote"

UPSTREAM_REF="origin/${BRANCH}"
if git rev-parse --verify --quiet "$UPSTREAM_REF" >/dev/null; then
  LOCAL_SHA="$(git rev-parse HEAD)"
  REMOTE_SHA="$(git rev-parse "$UPSTREAM_REF")"
  if [ "$LOCAL_SHA" != "$REMOTE_SHA" ]; then
    die "local $BRANCH ($(git rev-parse --short HEAD)) != $UPSTREAM_REF ($(git rev-parse --short "$UPSTREAM_REF")); push or pull first"
  fi
else
  die "$UPSTREAM_REF not found on origin; push the branch before releasing"
fi

# Refuse to clobber an existing release.
if git rev-parse --verify --quiet "refs/tags/${TAG}" >/dev/null; then
  die "tag $TAG already exists locally"
fi
# Capture first so a remote/auth failure can't masquerade as "tag absent".
REMOTE_TAGS="$(git ls-remote --tags origin "refs/tags/${TAG}")" || die "git ls-remote origin failed"
if printf '%s' "$REMOTE_TAGS" | grep -q "$TAG"; then
  die "tag $TAG already exists on origin"
fi

# ── Execute ──────────────────────────────────────────────────────────────────
run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY-RUN: $*"
  else
    "$@"
  fi
}

echo "Releasing $TAG at $(git rev-parse --short HEAD) on '$BRANCH'"
run git tag -a "$TAG" -m "Release $TAG"
run git push origin "$TAG"

if [ "$GH_RELEASE" -eq 1 ]; then
  if command -v gh >/dev/null 2>&1; then
    run gh release create "$TAG" --title "$TAG" --generate-notes
  else
    echo "release: --gh-release requested but 'gh' not found; tag pushed, GitHub Release skipped" >&2
  fi
fi

if [ "$DRY_RUN" -eq 1 ]; then
  echo "Dry run complete — no tag created."
else
  echo "Done. Clients on an older version will see the in-app update banner for $TAG."
fi
