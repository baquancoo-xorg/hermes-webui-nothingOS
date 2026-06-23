"""
Hermes Web UI -- Company Library: per-team document library for Founder.

Backend cho panel "Thư viện công ty": upload tài liệu theo phòng ban,
list/index, xem file, xóa (soft — chuyển .trash/), và notify CEO agent
qua Kanban card. Thư mục gốc: ~/company-library/<team>/ (dựng 2026-06-11,
luật agent nằm trong SOUL.md các profile lead/worker).

Quy ước index: library_index.json do CEO agent là sole-writer về mặt
NỘI DUNG agent (summary/acknowledge/action), nhưng WebUI (Founder) được
phép thêm entry mới khi upload và xóa entry — Founder là chủ thư viện.
Ghi index dùng fcntl lock + atomic replace để tránh đụng agent ghi cùng lúc.
"""
import fcntl
import hashlib
import json
import mimetypes
import os
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from api.helpers import j, bad

LIBRARY_ROOT = Path(os.environ.get("HERMES_COMPANY_LIBRARY", "~/company-library")).expanduser()

# team slug -> (kanban board, ceo/lead assignee) cho nút "Báo team đọc"
TEAMS = {
    "kaipay-content": ("kaipay-content", "kaipay-content-ceo"),
    "kaipay-video": ("kaipay-video-html", "kaipay-video-lead"),
    "quickmagic": ("quickmagic", "quickmagic-ceo"),
}

# loại tài liệu -> thư mục con. bao-cao là read-only từ UI (agent ghi).
DOC_TYPES = {
    "chien-luoc": "chien-luoc",
    "brand": "brand",
    "tham-chieu": "tham-chieu",
    "phan-hoi": "phan-hoi",
    "so-lieu": "so-lieu",
    "bao-cao": "bao-cao",
}
UPLOAD_TYPES = {k for k in DOC_TYPES if k != "bao-cao"}

_ALLOWED_EXT = {
    ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".txt", ".md",
    ".csv", ".json", ".docx", ".xlsx", ".pptx", ".mp4", ".mov", ".zip",
}
_INLINE_MIME_PREFIX = ("image/", "text/", "video/")
_INLINE_MIME_EXACT = {"application/pdf", "application/json"}


def _team_root(team: str) -> Path | None:
    if team not in TEAMS:
        return None
    root = (LIBRARY_ROOT / team).resolve()
    try:
        root.relative_to(LIBRARY_ROOT.resolve())
    except ValueError:
        return None
    return root


def _index_path(team_root: Path) -> Path:
    return team_root / "library_index.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load_index(team_root: Path, team: str) -> dict:
    p = _index_path(team_root)
    if not p.exists():
        return {"team": team, "version": 1, "updated_at": _now_iso(),
                "sole_writer": TEAMS[team][1], "entries": []}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        # index hỏng: không phá file gốc, trả bản rỗng kèm cờ để UI cảnh báo
        return {"team": team, "version": 1, "updated_at": _now_iso(),
                "sole_writer": TEAMS[team][1], "entries": [], "index_corrupt": True}


def _write_index_locked(team_root: Path, team: str, mutate) -> dict:
    """Đọc-sửa-ghi index dưới fcntl lock + atomic replace.

    mutate(index_dict) -> chỉnh in-place. Trả index sau khi ghi.
    """
    team_root.mkdir(parents=True, exist_ok=True)
    lock_path = team_root / ".library_index.lock"
    with open(lock_path, "w") as lock_fh:
        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
        try:
            idx = _load_index(team_root, team)
            mutate(idx)
            idx["updated_at"] = _now_iso()
            tmp = _index_path(team_root).with_suffix(".json.tmp")
            tmp.write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")
            os.replace(tmp, _index_path(team_root))
            return idx
        finally:
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)


def _slugify_filename(name: str) -> str:
    base = Path(name).stem
    ext = Path(name).suffix.lower()
    norm = unicodedata.normalize("NFD", base)
    norm = "".join(c for c in norm if unicodedata.category(c) != "Mn")
    norm = norm.replace("đ", "d").replace("Đ", "D")
    norm = re.sub(r"[^A-Za-z0-9._-]+", "-", norm).strip("-._") or "file"
    return (norm[:80] + ext).lower()


def _safe_member_path(team_root: Path, rel: str) -> Path | None:
    """Resolve rel bên trong team_root; chặn traversal/symlink-escape."""
    if not rel or rel.startswith(("/", "~")):
        return None
    target = (team_root / rel).resolve()
    try:
        target.relative_to(team_root)
    except ValueError:
        return None
    return target


def _entry_stale_check(team_root: Path, entry: dict) -> dict:
    """Đối soát nhẹ khi list: file mất -> missing:true (không sửa index)."""
    out = dict(entry)
    target = _safe_member_path(team_root, str(entry.get("path") or ""))
    out["missing"] = not (target and target.is_file())
    return out


# ── GET /api/library/index?team=<slug> ─────────────────────────────────────

def handle_library_index(handler, parsed):
    from urllib.parse import parse_qs
    qs = parse_qs(parsed.query)
    team = qs.get("team", [""])[0].strip()
    team_root = _team_root(team)
    if team_root is None:
        return bad(handler, "Unknown team", 404)
    idx = _load_index(team_root, team)
    entries = [_entry_stale_check(team_root, e) for e in idx.get("entries", [])]
    # bao-cao/ có thể chứa file agent ghi mà chưa vào index — liệt kê bổ sung
    indexed_paths = {str(e.get("path")) for e in entries}
    reports_extra = []
    rep_dir = team_root / "bao-cao"
    if rep_dir.is_dir():
        for f in sorted(rep_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if not f.is_file() or f.name.startswith("."):
                continue
            rel = f"bao-cao/{f.name}"
            if rel in indexed_paths:
                continue
            reports_extra.append({
                "id": f"fs-{hashlib.sha1(rel.encode()).hexdigest()[:10]}",
                "path": rel, "type": "bao-cao", "title": f.name,
                "note_founder": "", "summary": "(agent ghi, ngoài index)",
                "added_at": datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat(timespec="seconds"),
                "added_by": "agent", "status": "active",
                "acknowledged_by": [], "action_taken": None,
                "missing": False, "unindexed": True,
            })
    return j(handler, {
        "team": team, "teams": list(TEAMS.keys()),
        "updated_at": idx.get("updated_at"),
        "index_corrupt": bool(idx.get("index_corrupt")),
        "entries": entries + reports_extra,
    })


# ── POST /api/library/upload (multipart: team, doc_type, note, file) ───────

def handle_library_upload(handler):
    from api.config import MAX_UPLOAD_BYTES
    from api.upload import parse_multipart
    try:
        content_type = handler.headers.get("Content-Type", "")
        content_length = int(handler.headers.get("Content-Length", 0) or 0)
        if content_length > MAX_UPLOAD_BYTES:
            return j(handler, {"error": f"File quá lớn (tối đa {MAX_UPLOAD_BYTES // 1024 // 1024}MB)"}, status=413)
        fields, files = parse_multipart(handler.rfile, content_type, content_length)
        team = (fields.get("team") or "").strip()
        doc_type = (fields.get("doc_type") or "").strip()
        note = (fields.get("note") or "").strip()[:500]
        team_root = _team_root(team)
        if team_root is None:
            return bad(handler, "Unknown team", 404)
        if doc_type not in UPLOAD_TYPES:
            return bad(handler, "Loại tài liệu không hợp lệ")
        if "file" not in files:
            return bad(handler, "Thiếu file")
        filename, file_bytes = files["file"]
        if not filename:
            return bad(handler, "Thiếu tên file")
        safe = _slugify_filename(filename)
        if Path(safe).suffix not in _ALLOWED_EXT:
            return bad(handler, f"Đuôi file không hỗ trợ: {Path(safe).suffix}")
        sub = team_root / DOC_TYPES[doc_type]
        sub.mkdir(parents=True, exist_ok=True)
        dest = sub / safe
        if dest.exists():  # không ghi đè — thêm hậu tố thời gian
            dest = sub / f"{Path(safe).stem}-{time.strftime('%y%m%d%H%M%S')}{Path(safe).suffix}"
        dest.write_bytes(file_bytes)
        sha = hashlib.sha256(file_bytes).hexdigest()
        rel = str(dest.relative_to(team_root))
        entry = {
            "id": f"lib-{team.split('-')[0][:2]}{hashlib.sha1((rel + sha).encode()).hexdigest()[:8]}",
            "path": rel, "type": doc_type,
            "title": Path(filename).name,
            "note_founder": note, "summary": "",
            "sha256": sha, "added_at": _now_iso(),
            "added_by": "founder-webui",
            "status": "new", "acknowledged_by": [], "action_taken": None,
        }
        _write_index_locked(team_root, team, lambda idx: idx["entries"].append(entry))
        return j(handler, {"ok": True, "entry": entry})
    except ValueError as e:
        return j(handler, {"error": str(e)}, status=400)
    except Exception:
        import traceback
        print("[webui] library upload error: " + traceback.format_exc(), flush=True)
        return j(handler, {"error": "Upload thất bại"}, status=500)


# ── GET /api/library/file?team=&path=[&download=1] ─────────────────────────

def handle_library_file(handler, parsed):
    from urllib.parse import parse_qs
    qs = parse_qs(parsed.query)
    team = qs.get("team", [""])[0].strip()
    rel = qs.get("path", [""])[0]
    force_download = qs.get("download", [""])[0] == "1"
    team_root = _team_root(team)
    if team_root is None:
        return bad(handler, "Unknown team", 404)
    target = _safe_member_path(team_root, rel)
    if target is None or not target.is_file():
        return j(handler, {"error": "not found"}, status=404)
    mime = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
    inline = (mime.startswith(_INLINE_MIME_PREFIX) or mime in _INLINE_MIME_EXACT)
    if mime in ("text/html", "image/svg+xml"):  # chống XSS qua viewer
        inline = False
    data = target.read_bytes()
    handler.send_response(200)
    handler.send_header("Content-Type", mime if inline else "application/octet-stream")
    disp = "inline" if (inline and not force_download) else "attachment"
    handler.send_header("Content-Disposition", f'{disp}; filename="{target.name}"')
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.end_headers()
    handler.wfile.write(data)


# ── POST /api/library/delete {team, id} — soft delete vào .trash/ ──────────

def handle_library_delete(handler, body):
    team = (body.get("team") or "").strip()
    entry_id = (body.get("id") or "").strip()
    team_root = _team_root(team)
    if team_root is None:
        return bad(handler, "Unknown team", 404)
    if not entry_id:
        return bad(handler, "Thiếu id")
    removed = {}

    def mutate(idx):
        keep = []
        for e in idx["entries"]:
            if e.get("id") == entry_id:
                removed["entry"] = e
            else:
                keep.append(e)
        idx["entries"] = keep

    _write_index_locked(team_root, team, mutate)
    entry = removed.get("entry")
    if not entry:
        return bad(handler, "Không tìm thấy entry", 404)
    target = _safe_member_path(team_root, str(entry.get("path") or ""))
    if target and target.is_file():
        trash = team_root / ".trash"
        trash.mkdir(exist_ok=True)
        os.replace(target, trash / f"{time.strftime('%y%m%d%H%M%S')}-{target.name}")
    return j(handler, {"ok": True, "deleted": entry_id})


# ── POST /api/library/notify {team} — tạo Kanban card cho CEO/lead ─────────

def handle_library_notify(handler, body):
    team = (body.get("team") or "").strip()
    team_root = _team_root(team)
    if team_root is None:
        return bad(handler, "Unknown team", 404)
    board, assignee = TEAMS[team]
    idx = _load_index(team_root, team)
    new_entries = [e for e in idx.get("entries", []) if e.get("status") == "new"]
    if not new_entries:
        return j(handler, {"ok": False, "error": "Không có tài liệu mới (status=new) để báo."})
    lines = [
        f"- [{e.get('type')}] {e.get('title')} — {e.get('note_founder') or 'không ghi chú'} (path: {e.get('path')})"
        for e in new_entries[:20]
    ]
    title = f"Đọc tài liệu mới trong thư viện ({len(new_entries)} file)"
    task_body = (
        "Founder vừa thêm tài liệu vào Company Library "
        f"`~/company-library/{team}/`.\n\n"
        "Theo luật COMPANY LIBRARY trong SOUL: đọc full từng file mới đúng 1 lần, "
        "viết summary 5–10 dòng vào library_index.json, acknowledge, "
        "và với loại phan-hoi phải tạo task khắc phục hoặc ghi lý do không hành động.\n\n"
        "Danh sách file mới:\n" + "\n".join(lines)
    )
    try:
        from api.kanban_bridge import _create_task_payload
        result = _create_task_payload(
            {"title": title, "body": task_body, "assignee": assignee,
             "created_by": "founder-webui-library", "priority": 2},
            board=board,
        )
        task = result.get("task") or {}
        return j(handler, {"ok": True, "task_id": task.get("id"), "board": board,
                           "assignee": assignee, "new_count": len(new_entries)})
    except Exception as e:
        return j(handler, {"error": f"Không tạo được Kanban card: {e}"}, status=500)
