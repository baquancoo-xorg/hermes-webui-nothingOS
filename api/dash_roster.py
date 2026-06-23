"""Dashboard roster helper — READ-ONLY. Map board (kanban_board) -> profiles.

Nguồn chân lý là team-factory/registry.json (KHÔNG đoán theo prefix tên profile).
Lý do: board slug có thể KHÁC team slug (vd team "kaipay-video" dùng board
"kaipay-video-html") nên lọc profile bằng prefix board sẽ sót agent. registry.json
ghi rõ namespaces.kanban_board <-> namespaces.profiles / agents[].

KHÔNG ghi file. Chỉ đọc ~/.hermes/team-factory/registry.json. Lỗi đọc -> trả
found:false để caller (FE) fallback prefix cũ.
"""
from __future__ import annotations

import json
import os

REGISTRY_PATH = os.path.expanduser("~/.hermes/team-factory/registry.json")


def _load_registry() -> dict:
    """Đọc registry.json read-only. Thiếu/hỏng -> {} (không raise)."""
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        return {}


def get_roster_for_board(board_slug: str) -> dict:
    """Map board_slug (= kanban_board) -> list profiles từ registry.

    Trả: {"board", "found": bool, "team_slug": str|None,
          "profiles": [{"profile", "role", "display_name"}]}
    found=False => FE fallback prefix cũ.
    """
    reg = _load_registry()
    teams = reg.get("teams", {})
    if not isinstance(teams, dict):
        teams = {}

    for team_slug, team in teams.items():
        if not isinstance(team, dict):
            continue
        plan = team.get("plan") or {}
        ns = plan.get("namespaces") or {}
        if ns.get("kanban_board") != board_slug:
            continue

        # Khớp board. Ưu tiên agents[] (có role/display_name), bổ sung từ namespaces.profiles.
        agents = plan.get("agents") or []
        ns_profiles = ns.get("profiles") or []
        profiles: list[dict] = []
        seen: set[str] = set()

        for a in agents:
            if not isinstance(a, dict):
                continue
            prof = a.get("profile")
            if not prof or prof in seen:
                continue
            seen.add(prof)
            profiles.append({
                "profile": prof,
                "role": a.get("role"),
                "display_name": a.get("display_name"),
            })

        for prof in ns_profiles:
            if prof and prof not in seen:
                seen.add(prof)
                profiles.append({"profile": prof, "role": None, "display_name": None})

        return {
            "board": board_slug,
            "found": True,
            "team_slug": team_slug,
            "profiles": profiles,
        }

    return {"board": board_slug, "found": False, "team_slug": None, "profiles": []}
