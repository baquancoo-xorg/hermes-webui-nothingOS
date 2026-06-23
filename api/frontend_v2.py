"""Serve the embedded Hermes WebUI v2 SPA (single-process, no Node sidecar).

The v2 build lives at REPO_ROOT/frontend/dist (committed prebuilt). The backend
serves it under /v2/ and injects window.__HERMES_CONFIG__ (CSRF token + upload
limit) into the shell, mirroring what the legacy v1 shell did at routes.py:4719.
Paths under /v2/ are treated as public (auth handled client-side by LoginPage),
just like /static/.
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path
from urllib.parse import urlsplit

from api.config import REPO_ROOT
from api.helpers import bad

# Where the committed v2 build lives.
FRONTEND_DIST = (REPO_ROOT / "frontend" / "dist").resolve()

_MIME = {
    "html": "text/html; charset=utf-8",
    "js": "application/javascript; charset=utf-8",
    "css": "text/css; charset=utf-8",
    "json": "application/json; charset=utf-8",
    "svg": "image/svg+xml",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "ico": "image/x-icon",
    "gif": "image/gif",
    "webp": "image/webp",
    "woff": "font/woff",
    "woff2": "font/woff2",
    "ttf": "font/ttf",
    "map": "application/json; charset=utf-8",
    "txt": "text/plain; charset=utf-8",
    "webmanifest": "application/manifest+json",
}
_COMPRESSIBLE = {"html", "js", "css", "json", "svg", "map", "txt", "webmanifest"}


def is_v2_path(path: str) -> bool:
    """True for any request the v2 app owns: /v2 or /v2/..."""
    return path == "/v2" or path.startswith("/v2/")


def _csrf_token(handler) -> str:
    """Same contract as the legacy shell: token for an authed session, else ''."""
    try:
        from api.auth import (
            csrf_token_for_session,
            is_auth_enabled,
            parse_cookie,
            verify_session,
        )

        if not is_auth_enabled():
            return ""
        cookie_val = parse_cookie(handler)
        if cookie_val and verify_session(cookie_val):
            return csrf_token_for_session(cookie_val) or ""
    except Exception:
        pass
    return ""


def is_logged_in(handler) -> bool:
    """True when auth is disabled OR a valid session cookie is present."""
    try:
        from api.auth import is_auth_enabled, parse_cookie, verify_session
        if not is_auth_enabled():
            return True
        cookie_val = parse_cookie(handler)
        return bool(cookie_val and verify_session(cookie_val))
    except Exception:
        return False


def _inject_config(html: str, handler) -> str:
    """Insert window.__HERMES_CONFIG__ right after <head> so bootstrapCsrf finds it.

    The v2 dist/index.html does NOT ship this script (verified) — the v1 shell
    used to provide it. We synthesise it here.
    """
    try:
        from api.config import MAX_UPLOAD_BYTES as _max
    except Exception:
        _max = 0
    cfg = "{maxUploadBytes:%d,csrfToken:%s}" % (int(_max), json.dumps(_csrf_token(handler)))
    snippet = "<script>window.__HERMES_CONFIG__=%s;</script>" % cfg
    lower = html.lower()
    idx = lower.find("<head>")
    if idx != -1:
        pos = idx + len("<head>")
        return html[:pos] + snippet + html[pos:]
    # No <head> (shouldn't happen) — prepend so the token is still present.
    return snippet + html


def _send(handler, body: bytes, ct: str, *, immutable: bool, accept_enc: str, no_store: bool = False) -> bool:
    can_gz = ct.split(";")[0].split("/")[-1] in _COMPRESSIBLE or any(
        ct.startswith(p) for p in ("text/", "application/javascript", "application/json", "application/manifest")
    )
    use_gz = can_gz and "gzip" in (accept_enc or "").lower() and len(body) > 1024
    out = gzip.compress(body, 6) if use_gz else body
    handler.send_response(200)
    handler.send_header("Content-Type", ct)
    handler.send_header("Content-Length", str(len(out)))
    if no_store:
        handler.send_header("Cache-Control", "no-store")
    elif immutable:
        handler.send_header("Cache-Control", "public, max-age=31536000, immutable")
    else:
        handler.send_header("Cache-Control", "public, max-age=300")
    if use_gz:
        handler.send_header("Content-Encoding", "gzip")
        handler.send_header("Vary", "Accept-Encoding")
    handler.end_headers()
    try:
        handler.wfile.write(out)
    except (BrokenPipeError, ConnectionResetError):
        pass
    return True


def _serve_shell(handler) -> bool:
    """Serve index.html with __HERMES_CONFIG__ injected (SPA entry / fallback)."""
    index = FRONTEND_DIST / "index.html"
    if not index.is_file():
        return bad(handler, "v2 build not found (frontend/dist/index.html missing)", 500)
    html = _inject_config(index.read_text(encoding="utf-8"), handler)
    accept_enc = handler.headers.get("Accept-Encoding") or ""
    # shell must not be cached so a redeploy is picked up immediately
    return _send(handler, html.encode("utf-8"), _MIME["html"], immutable=False, accept_enc=accept_enc, no_store=True)


def serve(handler, parsed) -> bool:
    """Entry point: serve any /v2/... request. Returns True if handled."""
    # Strip the /v2 prefix → relative path inside dist.
    rel = parsed.path[len("/v2"):]
    if rel.startswith("/"):
        rel = rel[1:]
    rel = urlsplit(rel).path  # defensive: drop any stray query/fragment

    # Root or extension-less route → SPA shell (client router handles it).
    if rel == "" or "." not in rel.rsplit("/", 1)[-1]:
        return _serve_shell(handler)

    # Static asset: resolve + sandbox under FRONTEND_DIST.
    target = (FRONTEND_DIST / rel).resolve()
    try:
        target.relative_to(FRONTEND_DIST)
    except ValueError:
        return bad(handler, "not found", 404)
    if not target.is_file():
        # Unknown file under /v2/ → fall back to shell (SPA deep link with a dot).
        return _serve_shell(handler)

    ext = target.suffix.lower().lstrip(".")
    ct = _MIME.get(ext, "application/octet-stream")
    # Vite emits hashed filenames under assets/ → safe to cache immutably.
    immutable = "/assets/" in parsed.path
    accept_enc = handler.headers.get("Accept-Encoding") or ""
    return _send(handler, target.read_bytes(), ct, immutable=immutable, accept_enc=accept_enc)
