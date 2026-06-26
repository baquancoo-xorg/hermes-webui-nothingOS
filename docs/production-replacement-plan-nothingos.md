# Hermes WebUI NothingOS-inspired Replacement Plan

Status: staging validated on `127.0.0.1:8789`; production switch requires explicit Dominium approval.

## Scope

Replace the current production Hermes WebUI service with the redesigned `hermes-webui-next` app after staging approval.

## Current production facts

- Production app path: `/home/quancoo/apps/hermes-webui`
- Candidate app path: `/home/quancoo/apps/hermes-webui-next`
- Production port: `127.0.0.1:8787`
- Staging port used for QA: `127.0.0.1:8789`
- User systemd service: `hermes-webui.service`
- Runtime/session state must be preserved: `~/.hermes/webui`

## Pre-switch checklist

1. Confirm staging health:
   ```bash
   curl -fsS http://127.0.0.1:8789/health
   ```
2. Confirm v2 shell loads:
   ```bash
   curl -fsS http://127.0.0.1:8789/v2/ | grep -q "Hermes"
   ```
3. Confirm visual QA screenshot has been reviewed by Dominium.
4. Confirm target Git remote/fork is provided and redesign branch is pushed.
5. Confirm no secrets are committed:
   ```bash
   git status --short
   git diff -- . ':(exclude)frontend/dist/assets/index-Cgx1ooJL.js' | grep -Ei 'token|password|secret|api[_-]?key' || true
   ```
6. Stop staging process after review if it is no longer needed.

## Backup before production switch

```bash
TS=$(date +%Y%m%d-%H%M%S)
mkdir -p /home/quancoo/backups/hermes-webui-$TS
systemctl --user cat hermes-webui.service > /home/quancoo/backups/hermes-webui-$TS/hermes-webui.service.txt
cp -a /home/quancoo/apps/hermes-webui /home/quancoo/backups/hermes-webui-$TS/hermes-webui-app
```

Do not copy or print `.env` contents in logs/chat. Keep secrets local.

## Switch strategy

Preferred low-risk switch: update the user systemd service to point to `/home/quancoo/apps/hermes-webui-next/bootstrap.py` and port `8787`, then restart.

High-level steps after explicit approval:

```bash
systemctl --user stop hermes-webui.service
# Edit service ExecStart/WorkingDirectory to /home/quancoo/apps/hermes-webui-next
systemctl --user daemon-reload
systemctl --user start hermes-webui.service
curl -fsS http://127.0.0.1:8787/health
curl -fsS http://127.0.0.1:8787/v2/ | grep -q "Hermes"
```

## Post-switch QA

1. `/health` returns `status: ok`.
2. `/v2/` returns HTTP 200.
3. Login page renders NothingOS-inspired theme.
4. Authenticated chat can start a session.
5. Workspace/profile/session panels load.
6. Browser console has no uncaught errors.
7. `systemctl --user status hermes-webui.service` is active.

## Rollback

If health/login/chat fails:

```bash
systemctl --user stop hermes-webui.service
# Restore previous service file from backup or point service back to /home/quancoo/apps/hermes-webui
systemctl --user daemon-reload
systemctl --user start hermes-webui.service
curl -fsS http://127.0.0.1:8787/health
```

Keep `/home/quancoo/apps/hermes-webui` and `~/.hermes/webui` untouched until the new UI has run stably.
