"""Agent model/memory configuration inspection and safe editing.

This module is intentionally file-backed: Hermes profiles are the source of
truth, so the WebUI reads ``config.yaml``, ``.env``, and ``SOUL.md`` from every
profile home and writes only those config files. It does not touch memory
stores, Neo4j, or Qdrant data.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import socket
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover - WebUI requires PyYAML in normal runs
    yaml = None

# Import api.config for its Hermes-agent sys.path discovery side effect before
# importing api.profiles, which may import hermes_cli/agent modules.
from api import config as _webui_config  # noqa: F401
from api.profiles import get_profile_runtime_env, list_profiles_api

_SECRET_RE = re.compile(r"(key|token|secret|password|credential|cookie)", re.I)
_PROFILE_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_TEAM_RE = re.compile(r"(?:đội|team)\s+([A-Z][A-Z0-9_-]{2,})", re.I)
_HEADING_TEAM_RE = re.compile(r"^#\s*([A-Z][A-Z0-9_-]{2,})(?:\s+[—-]|\s*$)", re.M)
_ROLE_SUFFIXES = {
    "asset", "art-director", "backend", "ceo", "coder", "composer",
    "copywriter", "developer", "editor", "editor-qc", "frontend",
    "full-stack", "fullstack", "html-composer", "lead", "manager",
    "memory-steward", "normalizer", "ops", "orchestrator", "planner", "pm", "producer",
    "qa", "qc", "render-qc", "researcher", "reviewer", "scriptwriter",
    "storyboard-normalizer", "tester", "video-producer", "worker", "writer",
}
_ENV_EDIT_KEYS = {
    "GRAPHITI_EMBEDDING_BASE_URL", "GRAPHITI_EMBEDDING_DIM",
    "GRAPHITI_EMBEDDING_MODEL", "GRAPHITI_EMBEDDING_PROVIDER",
    "GRAPHITI_GROUP_ID", "GRAPHITI_LLM_BASE_URL", "GRAPHITI_LLM_MODEL",
    "GRAPHITI_RERANKER_MODE", "GRAPHITI_RERANKER_MODEL", "GRAPHITI_WRITE_MODE",
    "MEM0_LOCAL_COLLECTION", "MEM0_LOCAL_EMBED_BASE_URL",
    "MEM0_LOCAL_EMBED_DIMS", "MEM0_LOCAL_EMBED_MODEL",
    "MEM0_LOCAL_EMBED_PROVIDER", "MEM0_LOCAL_LLM_BASE_URL",
    "MEM0_LOCAL_LLM_MODEL", "MEM0_LOCAL_LLM_PROVIDER",
    "MEM0_LOCAL_QDRANT_ON_DISK", "MEM0_LOCAL_SYNC_INFER",
    "MEM0_LOCAL_USER_ID", "NEO4J_URI", "QDRANT_COLLECTION", "QDRANT_URL",
}


def _read_yaml(path: Path) -> dict[str, Any]:
    if yaml is None or not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _write_yaml_atomic(path: Path, data: dict[str, Any]) -> Path:
    if yaml is None:
        raise RuntimeError("PyYAML is required to write config.yaml")
    path.parent.mkdir(parents=True, exist_ok=True)
    backup = _backup_file(path)
    rendered = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(rendered)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
        # Validate it can be loaded after the atomic replace. Roll back if not.
        _read_yaml(path)
        return backup
    except Exception:
        try:
            if backup.exists():
                shutil.copy2(backup, path)
        finally:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass
        raise


def _backup_file(path: Path) -> Path:
    stamp = time.strftime("%Y%m%dT%H%M%S")
    backup = path.with_name(f"{path.name}.bak-{stamp}-{os.getpid()}-{time.time_ns()}")
    if path.exists():
        shutil.copy2(path, backup)
    else:
        backup.write_text("", encoding="utf-8")
    return backup


def _parse_env(path: Path) -> tuple[dict[str, str], list[str]]:
    values: dict[str, str] = {}
    lines: list[str] = []
    if not path.exists():
        return values, lines
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return values, []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values, lines


def _validate_env_updates(updates: dict[str, str]) -> dict[str, str]:
    clean: dict[str, str] = {}
    for key, value in updates.items():
        if key not in _ENV_EDIT_KEYS:
            continue
        value = str(value)
        if any(ch in value for ch in ("\n", "\r", "\x00")):
            raise ValueError(f"Invalid newline/control character in {key}")
        clean[key] = value
    return clean


def _write_env_atomic(path: Path, updates: dict[str, str]) -> Path | None:
    updates = _validate_env_updates(updates)
    if not updates:
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    backup = _backup_file(path)
    _, lines = _parse_env(path)
    seen: set[str] = set()
    new_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in updates:
                new_lines.append(f"{key}={updates[key]}")
                seen.add(key)
                continue
        new_lines.append(line)
    for key, value in updates.items():
        if key not in seen:
            new_lines.append(f"{key}={value}")
    content = "\n".join(new_lines).rstrip("\n") + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
        try:
            path.chmod(0o600)
        except Exception:
            pass
        return backup
    except Exception:
        try:
            if backup.exists():
                shutil.copy2(backup, path)
        finally:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass
        raise


def _redact_url(value: str) -> str:
    s = str(value or "")
    try:
        parsed = urllib.parse.urlsplit(s)
    except Exception:
        return s
    if not parsed.scheme or not parsed.netloc:
        return s
    host = parsed.hostname or ""
    if parsed.port:
        host = f"{host}:{parsed.port}"
    netloc = f"***@{host}" if (parsed.username or parsed.password) else parsed.netloc
    # Query strings frequently carry tokens; omit them from the browser payload.
    return urllib.parse.urlunsplit((parsed.scheme, netloc, parsed.path, "", ""))


def _mask_env(values: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in values.items():
        if _SECRET_RE.search(key):
            out[key] = "set" if value else "unset"
        else:
            out[key] = _redact_url(value)
    return out


def _first(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        s = str(value).strip()
        if s:
            return s
    return ""


def _classify_route(provider: str, base_url: str) -> str:
    raw = f"{provider} {base_url}".lower()
    if "127.0.0.1:8788" in raw or "localhost:8788" in raw:
        return "codex-proxy:8788"
    if "openrouter" in raw:
        return "OpenRouter"
    if not provider and not base_url:
        return "unknown"
    return "direct"


def _format_team_slug(slug: str) -> str:
    slug = slug.strip("-_ ").lower()
    if not slug:
        return "Default"
    if slug == "default":
        return "Default"
    if slug.startswith("kaipay"):
        return slug.upper()
    return " ".join(part.capitalize() if len(part) > 3 else part.upper() for part in slug.split("-") if part)


def _derive_team(profile_name: str, home: Path, env: dict[str, str]) -> str:
    explicit = _first(env.get("HERMES_TEAM"), env.get("AGENT_TEAM"), env.get("KAIPAY_VIDEO_TEAM"))
    if explicit:
        return explicit
    soul = ""
    try:
        soul = (home / "SOUL.md").read_text(encoding="utf-8", errors="ignore")[:8000]
    except Exception:
        pass
    for rx in (_TEAM_RE, _HEADING_TEAM_RE):
        match = rx.search(soul)
        if match:
            return match.group(1).upper()
    raw = profile_name.strip().lower()
    if raw == "default":
        return "Default"
    parts = raw.split("-")
    while len(parts) > 1:
        changed = False
        for n in range(min(3, len(parts) - 1), 0, -1):
            suffix = "-".join(parts[-n:])
            if suffix in _ROLE_SUFFIXES:
                parts = parts[:-n]
                changed = True
                break
        if not changed:
            break
    return _format_team_slug("-".join(parts))


def _cached_check_endpoint(cache: dict[str, dict[str, str]] | None, url: str, kind: str = "http") -> dict[str, str]:
    key = f"{kind}:{url}"
    if cache is None:
        return _check_endpoint(url, kind)
    if key not in cache:
        cache[key] = _check_endpoint(url, kind)
    return cache[key]


def _not_tested_health(url: str = "") -> dict[str, str]:
    if not url:
        return {"status": "missing", "detail": "not configured"}
    return {"status": "skipped", "detail": "not tested; click Test to probe this endpoint"}


def _endpoint(label: str, url: str, kind: str = "http", health_cache: dict[str, dict[str, str]] | None = None, include_health: bool = False) -> dict[str, Any]:
    if include_health:
        health = _cached_check_endpoint(health_cache, url, kind) if url else {"status": "missing", "detail": "not configured"}
    else:
        health = _not_tested_health(url)
    return {"label": label, "url": _redact_url(url), "kind": kind, "health": health}


def _check_endpoint(url: str, kind: str = "http", timeout: float = 0.7) -> dict[str, str]:
    url = str(url or "").strip()
    if not url:
        return {"status": "missing", "detail": "not configured"}
    parsed = urllib.parse.urlsplit(url)
    scheme = parsed.scheme.lower()
    if scheme in {"bolt", "neo4j"}:
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 7687
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return {"status": "reachable", "detail": f"tcp {host}:{port}"}
        except OSError as exc:
            return {"status": "unreachable", "detail": str(exc)[:160]}
    if scheme in {"http", "https"}:
        probe_url = url.rstrip("/")
        if ":6333" in probe_url:
            probe_url += "/collections"
        elif ":8788" in probe_url and not probe_url.endswith("/models"):
            probe_url += "/models" if probe_url.endswith("/v1") else "/v1/models"
        elif "openrouter.ai/api/v1" in probe_url and not probe_url.endswith("/models"):
            probe_url += "/models"
        elif ":8000" in probe_url or ":8001" in probe_url:
            probe_url += "/health"
        req = urllib.request.Request(probe_url, method="GET", headers={"User-Agent": "Hermes-WebUI-Agent-Config/1"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return {"status": "reachable", "detail": f"HTTP {resp.status}"}
        except urllib.error.HTTPError as exc:
            # HTTP reached the server even if auth/path rejects the probe.
            if 300 <= exc.code < 500:
                return {"status": "reachable", "detail": f"HTTP {exc.code}"}
            return {"status": "unreachable", "detail": f"HTTP {exc.code}"}
        except Exception as exc:
            return {"status": "unreachable", "detail": str(exc)[:160]}
    return {"status": "unknown", "detail": f"unsupported scheme {scheme or kind}"}


def _profile_payload(row: dict[str, Any], health_cache: dict[str, dict[str, str]] | None = None, include_health: bool = False) -> dict[str, Any]:
    name = str(row.get("name") or "default")
    home = Path(row.get("path") or "").expanduser()
    if not home:
        home = Path.home() / ".hermes"
    cfg_path = home / "config.yaml"
    env_path = home / ".env"
    cfg = _read_yaml(cfg_path)
    env, _ = _parse_env(env_path)
    runtime_env = get_profile_runtime_env(home)
    merged_env = {**env, **{k: v for k, v in runtime_env.items() if k not in env}}

    model_cfg = cfg.get("model", {}) if isinstance(cfg.get("model", {}), dict) else {}
    llm_provider = _first(model_cfg.get("provider"), row.get("provider"))
    llm_model = _first(model_cfg.get("default"), row.get("model"))
    llm_base_url = _first(model_cfg.get("base_url"))
    llm_route = _classify_route(llm_provider, llm_base_url)

    mem_cfg = cfg.get("memory", {}) if isinstance(cfg.get("memory", {}), dict) else {}
    honcho_cfg = cfg.get("honcho", {}) if isinstance(cfg.get("honcho", {}), dict) else {}

    embedding_provider = _first(
        merged_env.get("GRAPHITI_EMBEDDING_PROVIDER"),
        merged_env.get("MEM0_LOCAL_EMBED_PROVIDER"),
        "openai" if merged_env.get("GRAPHITI_EMBEDDING_MODEL") or merged_env.get("MEM0_LOCAL_EMBED_MODEL") else "",
    )
    embedding_model = _first(merged_env.get("GRAPHITI_EMBEDDING_MODEL"), merged_env.get("MEM0_LOCAL_EMBED_MODEL"))
    embedding_dim = _first(merged_env.get("GRAPHITI_EMBEDDING_DIM"), merged_env.get("MEM0_LOCAL_EMBED_DIMS"))
    collection = _first(merged_env.get("QDRANT_COLLECTION"), merged_env.get("MEM0_LOCAL_COLLECTION"), merged_env.get("GRAPHITI_GROUP_ID"))
    embedding_base_url = _first(merged_env.get("GRAPHITI_EMBEDDING_BASE_URL"), merged_env.get("MEM0_LOCAL_EMBED_BASE_URL"))

    stores: list[dict[str, Any]] = []
    memory_provider = _first(mem_cfg.get("provider"))
    memory_enabled = bool(mem_cfg.get("memory_enabled", True))
    def store_health(url: str) -> dict[str, str]:
        return _cached_check_endpoint(health_cache, url) if include_health else _not_tested_health(url)

    if memory_provider == "honcho" or honcho_cfg.get("base_url"):
        honcho_url = _first(honcho_cfg.get("base_url"))
        stores.append({"name": "Honcho", "enabled": memory_enabled and memory_provider == "honcho", "endpoint": _redact_url(honcho_url), "health": store_health(honcho_url)})
    if memory_provider.startswith("mem0") or any(k.startswith("MEM0_LOCAL_") for k in merged_env):
        qdrant_url = _first(merged_env.get("QDRANT_URL"))
        stores.append({"name": "Mem0", "enabled": memory_enabled and memory_provider.startswith("mem0"), "endpoint": _redact_url(qdrant_url), "health": store_health(qdrant_url)})
    if any(k.startswith("GRAPHITI_") for k in merged_env) or merged_env.get("NEO4J_URI"):
        graphiti_url = _first(merged_env.get("NEO4J_URI"), merged_env.get("GRAPHITI_LLM_BASE_URL"))
        stores.append({"name": "Graphiti", "enabled": True, "endpoint": _redact_url(graphiti_url), "health": store_health(graphiti_url)})
    if merged_env.get("QDRANT_URL") or collection:
        qdrant_url = _first(merged_env.get("QDRANT_URL"))
        stores.append({"name": "Qdrant", "enabled": bool(merged_env.get("QDRANT_URL")), "endpoint": _redact_url(qdrant_url), "collection": collection, "health": store_health(qdrant_url)})

    endpoints = []
    for label, url in [
        ("LLM", llm_base_url),
        ("Embedding", embedding_base_url),
        ("Qdrant", merged_env.get("QDRANT_URL", "")),
        ("Honcho", _first(honcho_cfg.get("base_url"))),
        ("Graphiti/Neo4j", merged_env.get("NEO4J_URI", "")),
        ("Graphiti LLM", merged_env.get("GRAPHITI_LLM_BASE_URL", "")),
        ("Mem0 LLM", merged_env.get("MEM0_LOCAL_LLM_BASE_URL", "")),
    ]:
        if url:
            endpoints.append(_endpoint(label, url, health_cache=health_cache, include_health=include_health))

    env_keys = {k: ("set" if v else "unset") for k, v in merged_env.items() if _SECRET_RE.search(k)}
    return {
        "name": name,
        "team": _derive_team(name, home, merged_env),
        "path": str(home),
        "config_path": str(cfg_path),
        "env_path": str(env_path),
        "llm": {"provider": llm_provider, "model": llm_model, "base_url": _redact_url(llm_base_url), "route": llm_route},
        "embedding": {"provider": embedding_provider, "model": embedding_model, "dim": embedding_dim, "collection": collection, "base_url": _redact_url(embedding_base_url), "route": _classify_route(embedding_provider, embedding_base_url)},
        "memory": {"provider": memory_provider, "enabled": memory_enabled, "stores": stores},
        "router_proxy": {"llm": llm_route, "embedding": _classify_route(embedding_provider, embedding_base_url)},
        "endpoints": endpoints,
        "secrets": env_keys,
        "honcho_base_url": _redact_url(_first(honcho_cfg.get("base_url"))),
        "editable_env": _mask_env({k: merged_env.get(k, "") for k in sorted(_ENV_EDIT_KEYS) if k in merged_env}),
    }


def list_agent_configs() -> dict[str, Any]:
    health_cache: dict[str, dict[str, str]] = {}
    agents = [_profile_payload(row, health_cache) for row in list_profiles_api()]
    teams_map: dict[str, list[dict[str, Any]]] = {}
    for agent in agents:
        teams_map.setdefault(agent["team"], []).append(agent)
    teams = []
    for team_name in sorted(teams_map, key=lambda n: (n != "Default", n.lower())):
        team_agents = sorted(teams_map[team_name], key=lambda a: a["name"])
        baseline = _team_baseline(team_agents)
        teams.append({"name": team_name, "agent_count": len(team_agents), "baseline": baseline, "agents": team_agents})
    return {"teams": teams, "agent_count": len(agents), "team_count": len(teams)}



_MEMORY_READ_METHODS = {
    "Honcho": {
        "method": "HTTP Honcho v3",
        "endpoints": [
            "GET /v3/workspaces/{workspace}/peers/{peer}/context",
            "GET /v3/workspaces/{workspace}/peers/{peer}/card",
            "POST /v3/workspaces/{workspace}/conclusions/list?size={limit}",
        ],
        "filters": "workspace from honcho.json; agent/source from aiPeer/observer_id; team = whole workspace",
        "provenance": "observer_id, observed_id, session_id, created_at",
    },
    "Mem0": {
        "method": "Read Mem0 OSS Qdrant backing collection with vector omitted",
        "endpoints": ["POST {QDRANT_URL}/collections/{MEM0_LOCAL_COLLECTION}/points/scroll"],
        "filters": "payload.agent_id/source_agent for agent; collection for team",
        "provenance": "payload.agent_id/source_agent, created_at/updated_at, point id",
    },
    "Qdrant": {
        "method": "Qdrant scroll API, payload only, with_vector=false",
        "endpoints": ["POST {QDRANT_URL}/collections/{QDRANT_COLLECTION}/points/scroll"],
        "filters": "collection plus payload source_agent/agent_id if present",
        "provenance": "payload.provenance, payload.source_agent/agent_id, payload timestamp fields",
    },
    "Graphiti": {
        "method": "Neo4j Bolt read-only Cypher against Graphiti graph",
        "endpoints": ["MATCH (n) WHERE n.group_id=$group RETURN labels(n), properties(n)"],
        "filters": "group_id/GRAPHITI_GROUP_ID for team; provenance.source_agent for agent",
        "provenance": "node provenance JSON, source_description, created_at/valid_at; status from truth_status/valid_to/superseded_by",
    },
}


def memory_read_methods() -> dict[str, Any]:
    """Return the Phase 0 read plan surfaced in the UI before build."""
    return {"stores": _MEMORY_READ_METHODS, "read_only": True, "default_limit": 50, "max_limit": 100}


def _safe_limit(raw: Any, default: int = 50, max_limit: int = 100) -> int:
    try:
        value = int(raw)
    except Exception:
        value = default
    return max(1, min(max_limit, value))


def _read_json_file(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _profile_row_payloads() -> list[dict[str, Any]]:
    health_cache: dict[str, dict[str, str]] = {}
    return [_profile_payload(row, health_cache) for row in list_profiles_api()]


def _agents_for_memory_query(profile_name: str = "", team_name: str = "") -> list[dict[str, Any]]:
    agents = _profile_row_payloads()
    if profile_name:
        agents = [a for a in agents if a.get("name") == profile_name]
        if not agents:
            raise FileNotFoundError("Profile not found")
    if team_name:
        agents = [a for a in agents if a.get("team") == team_name or a.get("teamName") == team_name]
        if not agents:
            raise FileNotFoundError("Team not found")
    return agents


def _agent_home(agent: dict[str, Any]) -> Path:
    return Path(agent.get("path") or "").expanduser()


def _profile_memory_context(agent: dict[str, Any]) -> dict[str, Any]:
    home = _agent_home(agent)
    cfg = _read_yaml(home / "config.yaml")
    env, _ = _parse_env(home / ".env")
    runtime_env = get_profile_runtime_env(home)
    merged_env = {**env, **{k: v for k, v in runtime_env.items() if k not in env}}
    honcho_file = _read_json_file(home / "honcho.json")
    honcho_cfg = cfg.get("honcho", {}) if isinstance(cfg.get("honcho", {}), dict) else {}
    return {
        "agent": agent,
        "home": home,
        "cfg": cfg,
        "env": merged_env,
        "honcho": honcho_file,
        "honcho_base_url": _first(honcho_file.get("baseUrl"), honcho_cfg.get("base_url"), "http://127.0.0.1:8001"),
        "honcho_workspace": _first(honcho_file.get("workspace"), merged_env.get("HONCHO_WORKSPACE"), agent.get("team"), "default"),
        "honcho_peer": _first(honcho_file.get("aiPeer"), merged_env.get("HONCHO_AI_PEER"), agent.get("name")),
        "qdrant_url": _first(merged_env.get("QDRANT_URL"), "http://127.0.0.1:6333"),
        "mem0_collection": _first(merged_env.get("MEM0_LOCAL_COLLECTION"), merged_env.get("QDRANT_COLLECTION"), agent.get("embedding", {}).get("collection")),
        "qdrant_collection": _first(merged_env.get("QDRANT_COLLECTION"), merged_env.get("MEM0_LOCAL_COLLECTION"), agent.get("embedding", {}).get("collection")),
        "graphiti_group": _first(merged_env.get("GRAPHITI_GROUP_ID"), agent.get("embedding", {}).get("collection")),
        "neo4j_uri": _first(merged_env.get("NEO4J_URI")),
        "neo4j_user": _first(merged_env.get("NEO4J_USER"), "neo4j"),
        "neo4j_password": _first(merged_env.get("NEO4J_PASSWORD"), merged_env.get("NEO4J_PASS"), merged_env.get("GRAPHITI_NEO4J_PASSWORD")),
    }


def _json_request(url: str, *, method: str = "GET", body: Any = None, timeout: float = 8.0) -> Any:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "Hermes-WebUI-Memory-Read/1"}
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read(2_000_000).decode("utf-8", "replace")
    return json.loads(raw) if raw else None


def _truncate(value: str, max_chars: int = 4000) -> str:
    s = str(value or "")
    return s if len(s) <= max_chars else s[:max_chars] + "…"


def _redact_text(value: Any) -> str:
    """Redact obvious secrets embedded in arbitrary memory text."""
    s = _truncate(str(value or ""))
    s = re.sub(r"(?i)([a-z][a-z0-9+.-]*://)([^\s/@:]+):([^\s/@]+)@", r"\1***@", s)
    s = re.sub(r"(?i)\b(api[_-]?key|token|secret|password|credential|cookie)=([^\s&]+)", r"\1=[REDACTED]", s)
    s = re.sub(r"\b(sk-[A-Za-z0-9_-]{16,})", "[REDACTED_API_KEY]", s)
    s = re.sub(r"\b(xox[baprs]-[A-Za-z0-9-]{16,})", "[REDACTED_TOKEN]", s)
    return s


def _sanitize_payload(value: Any, depth: int = 0) -> Any:
    if depth > 5:
        return "…"
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, val in value.items():
            k = str(key)
            lk = k.lower()
            if _SECRET_RE.search(k):
                out[k] = "set" if val else "unset"
            elif lk in {"vector", "embedding", "name_embedding", "embeddings"} or lk.endswith("_embedding"):
                try:
                    out[k] = f"[vector omitted: {len(val)} dims]"
                except Exception:
                    out[k] = "[vector omitted]"
            else:
                out[k] = _sanitize_payload(val, depth + 1)
        return out
    if isinstance(value, list):
        if len(value) > 60 and all(isinstance(x, (int, float)) for x in value[:20]):
            return f"[vector/list omitted: {len(value)} items]"
        return [_sanitize_payload(x, depth + 1) for x in value[:100]]
    if isinstance(value, str):
        return _redact_text(_redact_url(value))
    return value


def _parse_json_maybe(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    s = value.strip()
    if not s or s[0] not in "[{":
        return value
    try:
        return json.loads(s)
    except Exception:
        return value


def _payload_provenance(payload: dict[str, Any]) -> dict[str, Any]:
    prov = _parse_json_maybe(payload.get("provenance"))
    return prov if isinstance(prov, dict) else {}


def _record(store: str, ctx: dict[str, Any], *, item_id: Any = "", text: str = "", payload: Any = None,
            timestamp: str = "", source_agent: str = "", status: str = "current", kind: str = "memory") -> dict[str, Any]:
    agent = ctx.get("agent", {})
    safe_payload = _sanitize_payload(payload if payload is not None else {})
    return {
        "store": store,
        "id": str(item_id or ""),
        "team": agent.get("team", ""),
        "profile": agent.get("name", ""),
        "source_agent": source_agent or "unknown",
        "timestamp": str(timestamp or ""),
        "status": status or "current",
        "kind": kind,
        "text": _redact_text(_truncate(text, 2200)),
        "payload": safe_payload,
    }


def _source_matches(record_source: str, ctx: dict[str, Any], profile_filter: str) -> bool:
    if not profile_filter:
        return True
    src = str(record_source or "").lower()
    names = {str(profile_filter).lower(), str(ctx.get("agent", {}).get("name", "")).lower(), str(ctx.get("honcho_peer", "")).lower()}
    return src in names


def _honcho_records(ctx: dict[str, Any], limit: int, profile_filter: str, diagnostics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    base = str(ctx.get("honcho_base_url") or "").rstrip("/")
    workspace = urllib.parse.quote(str(ctx.get("honcho_workspace") or "default"), safe="")
    peer_raw = str(ctx.get("honcho_peer") or ctx.get("agent", {}).get("name") or "")
    peer = urllib.parse.quote(peer_raw, safe="")
    out: list[dict[str, Any]] = []
    if not base or not peer_raw:
        diagnostics.append({"store": "Honcho", "status": "skipped", "detail": "missing base_url or peer"})
        return out
    try:
        url = f"{base}/v3/workspaces/{workspace}/conclusions/list?size={limit}"
        data = _json_request(url, method="POST", body={}, timeout=10)
        for item in (data or {}).get("items", []):
            source = str(item.get("observer_id") or "")
            if not _source_matches(source, ctx, profile_filter):
                continue
            out.append(_record("Honcho", ctx, item_id=item.get("id"), text=item.get("content", ""), payload=item,
                               timestamp=item.get("created_at", ""), source_agent=source, kind="conclusion"))
            if len(out) >= limit:
                break
        diagnostics.append({"store": "Honcho", "status": "ok", "detail": f"conclusions read from workspace {ctx.get('honcho_workspace')}", "total": (data or {}).get("total")})
    except Exception as exc:
        diagnostics.append({"store": "Honcho", "status": "error", "detail": str(exc)[:180]})
    # Add compact context/card records for the selected agent only; do not make team view noisy.
    if profile_filter and len(out) < limit:
        for suffix, kind in [("context", "context"), ("card", "peer_card")]:
            try:
                data = _json_request(f"{base}/v3/workspaces/{workspace}/peers/{peer}/{suffix}", method="GET", timeout=8)
                text = ""
                if isinstance(data, dict):
                    text = _first(data.get("representation"), data.get("peer_card"), data.get("content"))
                if text:
                    out.append(_record("Honcho", ctx, item_id=f"{peer_raw}:{suffix}", text=text, payload=data,
                                       source_agent=peer_raw, kind=kind))
            except Exception:
                pass
    return out[:limit]


def _qdrant_scroll(qdrant_url: str, collection: str, limit: int, diagnostics: list[dict[str, Any]], store: str) -> list[dict[str, Any]]:
    if not qdrant_url or not collection:
        diagnostics.append({"store": store, "status": "skipped", "detail": "missing Qdrant URL or collection"})
        return []
    out: list[dict[str, Any]] = []
    offset = None
    scanned = 0
    try:
        while len(out) < limit and scanned < max(limit * 5, 50):
            body = {"limit": min(100, max(limit, 10)), "with_payload": True, "with_vector": False}
            if offset is not None:
                body["offset"] = offset
            data = _json_request(f"{qdrant_url.rstrip('/')}/collections/{urllib.parse.quote(collection, safe='')}/points/scroll", method="POST", body=body, timeout=10)
            result = (data or {}).get("result", {})
            points = result.get("points", []) or []
            out.extend(points)
            scanned += len(points)
            offset = result.get("next_page_offset")
            if not offset or not points:
                break
        diagnostics.append({"store": store, "status": "ok", "detail": f"scrolled {scanned} points from {collection}"})
    except Exception as exc:
        diagnostics.append({"store": store, "status": "error", "detail": str(exc)[:180], "collection": collection})
    return out


def _qdrant_records(ctx: dict[str, Any], limit: int, profile_filter: str, diagnostics: list[dict[str, Any]], store: str, collection: str) -> list[dict[str, Any]]:
    points = _qdrant_scroll(str(ctx.get("qdrant_url") or ""), collection, limit, diagnostics, store)
    out: list[dict[str, Any]] = []
    for point in points:
        payload = point.get("payload", {}) if isinstance(point, dict) else {}
        if not isinstance(payload, dict):
            payload = {"payload": payload}
        prov = _payload_provenance(payload)
        source = _first(payload.get("source_agent"), payload.get("agent_id"), prov.get("source_agent"), payload.get("role"))
        if not _source_matches(source, ctx, profile_filter):
            continue
        timestamp = _first(payload.get("created_at"), payload.get("updated_at"), payload.get("timestamp"), prov.get("timestamp"))
        text = _first(payload.get("memory"), payload.get("data"), payload.get("text"), payload.get("fact"), payload.get("summary"), json.dumps(_sanitize_payload(payload), ensure_ascii=False))
        kind = "mem0_memory" if store == "Mem0" else "qdrant_payload"
        out.append(_record(store, ctx, item_id=point.get("id"), text=text, payload={"collection": collection, **payload},
                           timestamp=timestamp, source_agent=source, kind=kind))
        if len(out) >= limit:
            break
    return out


def _neo4j_to_plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _neo4j_to_plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_neo4j_to_plain(v) for v in value]
    if hasattr(value, "iso_format"):
        try:
            return value.iso_format()
        except Exception:
            return str(value)
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            return str(value)
    return value


def _graphiti_status(props: dict[str, Any]) -> str:
    content = _parse_json_maybe(props.get("content"))
    if isinstance(content, dict):
        status = _first(content.get("truth_status"), content.get("status"))
        if status:
            return status
        if content.get("valid_to") or content.get("superseded_by"):
            return "superseded"
    status = _first(props.get("truth_status"), props.get("status"))
    if status:
        return status
    if props.get("valid_to") or props.get("invalid_at") or props.get("expired_at") or props.get("superseded_by"):
        return "superseded"
    return "current"


def _graphiti_records(ctx: dict[str, Any], limit: int, profile_filter: str, diagnostics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    uri = str(ctx.get("neo4j_uri") or "")
    if not uri:
        diagnostics.append({"store": "Graphiti", "status": "skipped", "detail": "missing NEO4J_URI"})
        return []
    try:
        from neo4j import GraphDatabase  # type: ignore
    except Exception as exc:
        diagnostics.append({"store": "Graphiti", "status": "error", "detail": f"neo4j package unavailable: {exc}"})
        return []
    raw_groups = [
        str(ctx.get("graphiti_group") or ""),
        str(ctx.get("honcho_workspace") or ""),
        str(ctx.get("agent", {}).get("team") or ""),
    ]
    groups: list[str] = []
    for raw in raw_groups:
        value = raw.strip()
        if not value:
            continue
        candidates = {value, value.replace("-", "_"), value.replace("_", "-")}
        if value.endswith("_mem0"):
            candidates.add(value[:-5])
        if "_mem0_" in value:
            candidates.add(value.split("_mem0_", 1)[0])
        for candidate in candidates:
            c = candidate.strip().lower()
            if c and c not in groups:
                groups.append(c)
    out: list[dict[str, Any]] = []
    query = """
    MATCH (n)
    WHERE (size($groups) = 0 OR toLower(n.group_id) IN $groups)
      AND any(label IN labels(n) WHERE label IN ['KaipayFact','Episodic','Entity','Community','Saga'])
    RETURN labels(n) AS labels, properties(n) AS props
    ORDER BY coalesce(n.created_at, n.valid_at) DESC
    LIMIT $limit
    """
    try:
        driver = GraphDatabase.driver(uri, auth=(ctx.get("neo4j_user") or "neo4j", ctx.get("neo4j_password") or ""))
        with driver.session() as session:
            rows = list(session.run(query, groups=groups, limit=max(limit * 5, 50)))
        driver.close()
        for row in rows:
            labels = list(row.get("labels") or [])
            props = _neo4j_to_plain(dict(row.get("props") or {}))
            prov = _payload_provenance(props)
            content = _parse_json_maybe(props.get("content"))
            content_obj = content if isinstance(content, dict) else {}
            source = _first(prov.get("source_agent"), props.get("source_agent"), content_obj.get("source_agent"), props.get("source"))
            if not _source_matches(source, ctx, profile_filter):
                continue
            text = _first(props.get("fact"), props.get("summary"), content_obj.get("statement"), props.get("content"), props.get("name"))
            timestamp = _first(prov.get("timestamp"), props.get("created_at"), props.get("valid_at"), content_obj.get("episode_date"))
            payload = {"labels": labels, **props}
            out.append(_record("Graphiti", ctx, item_id=props.get("uuid") or props.get("name"), text=text, payload=payload,
                               timestamp=timestamp, source_agent=source, status=_graphiti_status(props), kind="graph_node"))
            if len(out) >= limit:
                break
        diagnostics.append({"store": "Graphiti", "status": "ok", "detail": f"read {len(out)} nodes from {_redact_url(uri)} groups={','.join(groups) or '*'}"})
    except Exception as exc:
        diagnostics.append({"store": "Graphiti", "status": "error", "detail": str(exc)[:180], "uri": _redact_url(uri)})
    return out


def read_agent_memory(profile_name: str = "", team_name: str = "", store: str = "all", limit: Any = 50, _allow_team_fallback: bool = True) -> dict[str, Any]:
    """Read agent/team memory stores without mutating them."""
    limit_n = _safe_limit(limit)
    store_filter = str(store or "all").lower()
    profile_filter = str(profile_name or "").strip()
    team_filter = str(team_name or "").strip()
    agents = _agents_for_memory_query(profile_filter, team_filter)
    records: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    scanned_sources: set[tuple[str, str, str]] = set()
    for agent in agents:
        ctx = _profile_memory_context(agent)
        selected = []
        def should_scan(kind: str, endpoint: str, bucket: str) -> bool:
            if profile_filter:
                return True
            key = (kind, endpoint or "", bucket or "")
            if key in scanned_sources:
                return False
            scanned_sources.add(key)
            return True
        if store_filter in {"all", "honcho"} and should_scan("Honcho", str(ctx.get("honcho_base_url") or ""), str(ctx.get("honcho_workspace") or "")):
            selected.extend(_honcho_records(ctx, limit_n, profile_filter, diagnostics))
        if store_filter in {"all", "mem0"} and should_scan("Mem0", str(ctx.get("qdrant_url") or ""), str(ctx.get("mem0_collection") or "")):
            selected.extend(_qdrant_records(ctx, limit_n, profile_filter, diagnostics, "Mem0", str(ctx.get("mem0_collection") or "")))
        if store_filter in {"all", "qdrant"} and should_scan("Qdrant", str(ctx.get("qdrant_url") or ""), str(ctx.get("qdrant_collection") or "")):
            selected.extend(_qdrant_records(ctx, limit_n, profile_filter, diagnostics, "Qdrant", str(ctx.get("qdrant_collection") or "")))
        if store_filter in {"all", "graphiti"} and should_scan("Graphiti", str(ctx.get("neo4j_uri") or ""), str(ctx.get("graphiti_group") or ctx.get("honcho_workspace") or "")):
            selected.extend(_graphiti_records(ctx, limit_n, profile_filter, diagnostics))
        for rec in selected:
            key = (rec.get("store", ""), rec.get("id", ""), rec.get("text", "")[:120])
            if key in seen:
                continue
            seen.add(key)
            records.append(rec)
            if len(records) >= limit_n and profile_filter:
                break
        if len(records) >= limit_n and profile_filter:
            break

    records.sort(key=lambda r: str(r.get("timestamp") or ""), reverse=True)
    records = records[:limit_n]
    by_store: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for rec in records:
        by_store[rec["store"]] = by_store.get(rec["store"], 0) + 1
        by_status[rec["status"]] = by_status.get(rec["status"], 0) + 1
    if profile_filter and not records and _allow_team_fallback and agents:
        fallback_team = str(agents[0].get("team") or "").strip()
        if fallback_team:
            fallback = read_agent_memory(team_name=fallback_team, store=store_filter, limit=limit_n, _allow_team_fallback=False)
            if fallback.get("records"):
                for rec in fallback["records"]:
                    rec["scope_match"] = "team_fallback"
                fallback["filters"] = {"profile": profile_filter, "team": team_filter, "store": store_filter, "limit": limit_n}
                fallback["fallback"] = {
                    "used": True,
                    "reason": "No records had source_agent/observer_id matching this agent; showing shared team-scope memory instead.",
                    "team": fallback_team,
                    "strict_agent_record_count": 0,
                }
                fallback.setdefault("summary", {})["agent_strict_record_count"] = 0
                return fallback
    return {
        "ok": True,
        "read_only": True,
        "methods": _MEMORY_READ_METHODS,
        "filters": {"profile": profile_filter, "team": team_filter, "store": store_filter, "limit": limit_n},
        "summary": {"record_count": len(records), "by_store": by_store, "by_status": by_status, "agents_scanned": len(agents)},
        "fallback": {"used": False},
        "records": records,
        "diagnostics": diagnostics,
    }

def _team_baseline(agents: list[dict[str, Any]]) -> dict[str, Any]:
    def counts(path: list[str]) -> dict[str, int]:
        out: dict[str, int] = {}
        for agent in agents:
            value: Any = agent
            for key in path:
                value = value.get(key, {}) if isinstance(value, dict) else ""
            s = str(value or "")
            out[s] = out.get(s, 0) + 1
        return out
    return {
        "llm_route": counts(["llm", "route"]),
        "llm_model": counts(["llm", "model"]),
        "embedding_model": counts(["embedding", "model"]),
        "embedding_dim": counts(["embedding", "dim"]),
        "collection": counts(["embedding", "collection"]),
    }


def _resolve_agent_home(profile_name: str) -> Path:
    if not _PROFILE_RE.fullmatch(profile_name):
        raise ValueError("Invalid profile name")
    for row in list_profiles_api():
        if row.get("name") == profile_name:
            return Path(row.get("path") or "").expanduser()
    raise FileNotFoundError("Profile not found")


def save_agent_config(profile_name: str, patch: dict[str, Any], confirm: bool = False) -> dict[str, Any]:
    if not confirm:
        raise PermissionError("Saving agent config requires explicit confirmation")
    home = _resolve_agent_home(profile_name)
    cfg_path = home / "config.yaml"
    env_path = home / ".env"
    cfg = _read_yaml(cfg_path)
    backups: list[str] = []

    model = patch.get("model") if isinstance(patch.get("model"), dict) else {}
    if model:
        cfg.setdefault("model", {})
        if not isinstance(cfg["model"], dict):
            cfg["model"] = {}
        for key in ("provider", "default", "base_url", "context_length"):
            if key in model:
                cfg["model"][key] = model[key]

    memory = patch.get("memory") if isinstance(patch.get("memory"), dict) else {}
    if memory:
        cfg.setdefault("memory", {})
        if not isinstance(cfg["memory"], dict):
            cfg["memory"] = {}
        for key in ("provider", "memory_enabled", "user_profile_enabled"):
            if key in memory:
                cfg["memory"][key] = memory[key]

    honcho = patch.get("honcho") if isinstance(patch.get("honcho"), dict) else {}
    if honcho:
        cfg.setdefault("honcho", {})
        if not isinstance(cfg["honcho"], dict):
            cfg["honcho"] = {}
        if "base_url" in honcho:
            cfg["honcho"]["base_url"] = honcho["base_url"]

    env_updates_obj = patch.get("env")
    env_updates_raw = env_updates_obj if isinstance(env_updates_obj, dict) else {}
    env_updates = _validate_env_updates({str(k): str(v) for k, v in env_updates_raw.items()})

    cfg_backup: Path | None = None
    try:
        cfg_backup = _write_yaml_atomic(cfg_path, cfg)
        backups.append(str(cfg_backup))
        env_backup = _write_env_atomic(env_path, env_updates)
        if env_backup:
            backups.append(str(env_backup))
    except Exception:
        if cfg_backup and cfg_backup.exists():
            try:
                shutil.copy2(cfg_backup, cfg_path)
            except Exception:
                pass
        raise

    agent = _profile_payload({"name": profile_name, "path": str(home)})
    return {"ok": True, "profile": profile_name, "backups": backups, "agent": agent}


def test_agent_config(profile_name: str) -> dict[str, Any]:
    home = _resolve_agent_home(profile_name)
    agent = _profile_payload({"name": profile_name, "path": str(home)}, health_cache={}, include_health=True)
    checks: list[dict[str, Any]] = []

    llm = agent["llm"]
    checks.append(_test_openai_compatible("LLM", llm.get("base_url"), llm.get("model"), _env_for_home(home), embeddings=False))

    emb = agent["embedding"]
    checks.append(_test_openai_compatible("Embedding", emb.get("base_url"), emb.get("model"), _env_for_home(home), embeddings=True))

    for store in agent["memory"]["stores"]:
        checks.append({"name": store["name"], "status": store.get("health", {}).get("status", "unknown"), "detail": store.get("health", {}).get("detail", "")})
    return {"ok": all(c.get("status") in {"pass", "reachable", "skipped"} for c in checks), "profile": profile_name, "checks": checks}


def _env_for_home(home: Path) -> dict[str, str]:
    env, _ = _parse_env(home / ".env")
    return env


def _api_key_for_base(env: dict[str, str], base_url: str) -> str:
    raw = str(base_url or "").lower()
    if "openrouter" in raw:
        return env.get("OPENROUTER_API_KEY", "")
    return env.get("OPENAI_API_KEY", "") or env.get("MEM0_LOCAL_LLM_API_KEY", "")


def _test_openai_compatible(label: str, base_url: str, model: str, env: dict[str, str], embeddings: bool = False) -> dict[str, str]:
    if not base_url:
        return {"name": label, "status": "skipped", "detail": "no base_url configured"}
    if "chatgpt.com/backend-api/codex" in str(base_url).lower():
        return {"name": label, "status": "skipped", "detail": "OpenAI Codex OAuth backend is not OpenAI-compatible; Hermes owns the live generation path"}
    health = _check_endpoint(base_url)
    if health.get("status") != "reachable":
        return {"name": label, "status": "unreachable", "detail": health.get("detail", "")}
    # The WebUI avoids exposing secrets. For public providers, require a key in
    # the profile .env; for local OpenAI-compatible proxy, /models reachability is
    # enough to prove the route is usable without spending tokens.
    raw = base_url.lower()
    if "127.0.0.1" in raw or "localhost" in raw:
        return {"name": label, "status": "pass", "detail": "local OpenAI-compatible endpoint reachable"}
    key = _api_key_for_base(env, base_url)
    if not key:
        return {"name": label, "status": "skipped", "detail": "API key not set in profile .env"}
    if "openrouter" in raw:
        auth_url = base_url.rstrip("/") + "/auth/key"
        req = urllib.request.Request(
            auth_url,
            method="GET",
            headers={"Authorization": f"Bearer {key}", "User-Agent": "Hermes-WebUI-Agent-Config/1"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return {"name": label, "status": "pass", "detail": f"OpenRouter key accepted (HTTP {resp.status})"}
        except urllib.error.HTTPError as exc:
            return {"name": label, "status": "fail", "detail": f"OpenRouter auth HTTP {exc.code}"}
        except Exception as exc:
            # Endpoint health already passed; do not make transient auth probes block the panel.
            return {"name": label, "status": "reachable", "detail": f"endpoint reachable; auth probe timed out: {str(exc)[:120]}"}

    return {"name": label, "status": "pass", "detail": "endpoint reachable and API key configured"}
