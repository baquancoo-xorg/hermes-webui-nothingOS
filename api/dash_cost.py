"""Dashboard cost helper — READ-ONLY. Tính cost Opus thật từ claude -p jsonl.

Backend v1 parser cũ (_parse_claude_code_jsonl) KHÔNG trả usage token nên không
tính được cost. Helper này tự đọc jsonl, lấy message.usage, tính cost theo giá
proxy (Opus chuẩn / 3, đã verify khớp số liệu thật A-05), map cwd -> task_id ->
agent (best-effort qua kanban assignee).

KHÔNG ghi file. KHÔNG sửa logic import cũ. Chỉ đọc ~/.claude/projects.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

# Giá proxy nội bộ = Opus chuẩn / 3 ($/1M token). Verified A-05 (smoke $0.193, code $0.247).
PRICE = {"input": 5.0, "cache_write": 6.25, "cache_read": 0.5, "output": 25.0}

_MAX_FILES = 2000
_MAX_FILE_BYTES = 64 * 1024 * 1024


def _projects_dir() -> Path | None:
    root = Path(os.path.expanduser("~/.claude/projects"))
    try:
        if root.is_symlink() or not root.is_dir():
            return None
        return root.resolve(strict=False)
    except OSError:
        return None


def _cost_from_usage(u: dict) -> float:
    if not isinstance(u, dict):
        return 0.0
    return (
        (u.get("input_tokens", 0) or 0) * PRICE["input"] / 1e6
        + (u.get("cache_creation_input_tokens", 0) or 0) * PRICE["cache_write"] / 1e6
        + (u.get("cache_read_input_tokens", 0) or 0) * PRICE["cache_read"] / 1e6
        + (u.get("output_tokens", 0) or 0) * PRICE["output"] / 1e6
    )


def _iter_jsonl_files(root: Path):
    yielded = 0
    try:
        for project_dir in sorted(root.iterdir(), key=lambda p: p.name):
            if yielded >= _MAX_FILES:
                return
            try:
                if project_dir.is_symlink() or not project_dir.is_dir():
                    continue
                for path in sorted(project_dir.iterdir(), key=lambda p: p.name):
                    if yielded >= _MAX_FILES:
                        return
                    if path.is_symlink() or not path.is_file() or path.suffix.lower() != ".jsonl":
                        continue
                    try:
                        if path.stat().st_size > _MAX_FILE_BYTES:
                            continue
                    except OSError:
                        continue
                    yielded += 1
                    yield path
            except OSError:
                continue
    except OSError:
        return


def _task_id_from_cwd(cwd: str | None) -> str | None:
    """Map cwd -> task_id. Worktree/workspace path chứa .worktrees/<task> hoặc workspaces/<task>."""
    if not cwd:
        return None
    for marker in (".worktrees/", "workspaces/"):
        if marker in cwd:
            tail = cwd.split(marker, 1)[1]
            tid = tail.split("/", 1)[0]
            if tid.startswith("t_"):
                return tid
    return None


def compute_cost(assignee_by_task: dict[str, str] | None = None) -> dict:
    """Tổng cost + per-agent (best-effort). assignee_by_task: map task_id -> agent từ kanban."""
    root = _projects_dir()
    if root is None:
        return {"total_cost_usd": 0.0, "per_agent": {}, "unmapped_cost_usd": 0.0, "note": "no claude projects dir"}

    assignee_by_task = assignee_by_task or {}
    total = 0.0
    unmapped = 0.0
    per_agent: dict[str, float] = {}

    for path in _iter_jsonl_files(root):
        try:
            file_cost = 0.0
            cwd = None
            with path.open("r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                    except (ValueError, TypeError):
                        continue
                    if not isinstance(d, dict):
                        continue
                    if d.get("cwd") and cwd is None:
                        cwd = d["cwd"]
                    msg = d.get("message")
                    usage = msg.get("usage") if isinstance(msg, dict) else None
                    if usage:
                        file_cost += _cost_from_usage(usage)
            if file_cost <= 0:
                continue
            total += file_cost
            task_id = _task_id_from_cwd(cwd)
            agent = assignee_by_task.get(task_id) if task_id else None
            if agent:
                per_agent[agent] = round(per_agent.get(agent, 0.0) + file_cost, 4)
            else:
                unmapped += file_cost
        except OSError:
            continue

    return {
        "total_cost_usd": round(total, 4),
        "per_agent": {k: round(v, 4) for k, v in per_agent.items()},
        "unmapped_cost_usd": round(unmapped, 4),
        "price_note": "proxy Opus/3 (input 5/cache_write 6.25/cache_read 0.5/output 25 per 1M)",
    }
