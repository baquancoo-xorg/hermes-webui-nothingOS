---
title: "Diagnostic — NothingOS WebUI blank page on VPS vs upstream Tungbillee"
date: 2026-06-27
type: diagnostic
status: needs-vps-evidence
symptom: "server chạy nhưng mở web trắng/lỗi, trên Linux/VPS"
suspect_commit: c82e2f9 (NothingOS rewrite, pre-lightmode)
upstream: nesquena/hermes-webui (master)
---

# Diagnostic: Blank page on VPS

## What I verified (code is clean)

| Check | Result |
|---|---|
| Fresh `git clone` @ c82e2f9 boots + serves `/` | ✅ 200, no errors (Python 3.11) |
| `import api.routes` + `server.py` | ✅ OK |
| Orphan refs `frontend_v2`/`frontend/dist`/`FRONTEND_DIST` | ✅ none |
| `tokens.css` + `os-widgets.js` committed, not gitignored | ✅ |
| All `static/*.js` referenced in index.html exist | ✅ 13/13 |
| Asset paths relative (`static/...`, proxy-safe) | ✅ 21 relative, 0 absolute |
| Serve `/` model vs upstream | ✅ identical (placeholders, CSRF, inject_extension_tags) |
| Local render (Orca browser) | ✅ shell renders, no blank |

**Conclusion: the rewrite is code-clean. It moved the fork CLOSER to upstream**
(upstream also serves `static/index.html`; the `frontend/dist` v2 SPA was a fork
addition that the rewrite removed). I cannot reproduce the blank page locally.

## Ranked hypotheses (need VPS evidence to confirm)

### H1 — Stale service worker from the v2 era (MOST LIKELY if VPS was updated, not fresh)
- If the browser previously loaded the **v2 SPA** build, it registered `sw.js`
  and cached a v2 shell that referenced `/v2/assets/*.js` chunks.
- After updating to the v1-shell rewrite, those v2 chunks are **deleted** →
  the cached shell loads but its scripts 404 → **blank page**.
- `CACHE_NAME = hermes-shell-<WEBUI_VERSION>`. If `WEBUI_VERSION` resolves to
  `'unknown'` (no `.git` — e.g. installed from a ZIP/tarball, not `git clone`),
  the cache key never changes and the stale cache is never purged.
- **Test:** on the VPS browser → DevTools → Application → Service Workers →
  "Unregister" + Clear storage → hard reload. If page appears → confirmed H1.

### H2 — WEBUI_VERSION = 'unknown' (install method without .git)
- `_detect_webui_version()` = `git describe`. No `.git` and no `api/_version.py`
  → `'unknown'`. Assets cache under a constant `?v=unknown`; SW cache constant.
- **Test:** `curl -s http://<vps>:8787/ | grep -o '?v=[^"&]*' | head` — if it
  shows `?v=unknown`, install lacks git metadata.

### H3 — 302 redirect to /login under a reverse proxy (only if auth enabled)
- The rewrite ADDED a server-side `302 → /login` for unauthed `/` (upstream does
  NOT — it serves the shell with `csrfToken:""` and lets the client handle auth).
- Behind a path-rewriting proxy, `Location: /login` (absolute) can land outside
  the app's mount → blank/404. Upstream's no-redirect approach is proxy-safer.
- **Test:** `curl -sI http://<vps>:8787/` with auth on → check `Location` header.

### H4 — Python 3.9 (breaks bootstrap entirely, but that's "server won't run", not blank)
- Whole codebase + `bootstrap.py` use `str | None` (needs Python ≥3.10).
- User said "server chạy" → so Python is ≥3.10 on the VPS. Likely NOT the cause
  here, but worth confirming: `python3 --version`.

## What to capture on the VPS (exact commands)

```bash
# 1. Server-side: is the shell served correctly?
curl -s -i http://127.0.0.1:8787/ | head -20
curl -s http://127.0.0.1:8787/ | grep -c '__CSRF_TOKEN_JSON__\|__WEBUI_VERSION__'   # want 0
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8787/static/boot.js        # want 200
curl -s http://127.0.0.1:8787/ | grep -o '?v=[^"&]*' | head -1                       # version token

# 2. Python version (must be >=3.10)
python3 --version

# 3. Browser-side (the decisive evidence): open the VPS URL, F12 →
#    - Console tab: copy ALL red errors
#    - Network tab: any request showing 404 / red (especially *.js / *.css)
#    - Application → Service Workers: is one registered? what scope?
```

## Proactive fixes worth doing regardless (small, safe)
1. **SW precache gap:** `sw.js` SHELL_ASSETS lists `style.css` but not the new
   `tokens.css` / `os-widgets.js`. Add them so offline/PWA shell is complete.
2. **(Optional, reduces H3 risk):** match upstream — drop the server-side
   `302 → /login` and let the v1 client handle unauthed state (serve shell with
   empty CSRF). Lower proxy risk, fewer moving parts.

## Open questions (for Sếp)
- VPS install method: `git clone`? ZIP/tarball? Docker?
- Was the VPS browser used to view the v2 SPA before the rewrite? (→ H1)
- Is `HERMES_WEBUI_PASSWORD` set on the VPS? (→ H3 only matters if yes)
- Behind nginx/caddy/Cloudflare reverse proxy at a subpath?
