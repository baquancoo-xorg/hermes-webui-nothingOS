# NothingOS WebUI — Deploy, Switch & Rollback

Triển khai bản NothingOS này để thay thế WebUI đang chạy. Nền là nesquena stable
+ 4 tính năng Tungbillee + design NothingOS. Không có React SPA, không có `/v2`.

## Yêu cầu
- **Python ≥ 3.11** (bắt buộc). Bản này dùng cú pháp 3.10+; `bootstrap.py` tự dò
  `python3.11/3.12/3.13`. Máy chỉ có `python3` = 3.9 → bootstrap báo lỗi rõ ràng.
- Engine `hermes-agent` cài sẵn ở `~/.hermes/hermes-agent` (như upstream).
- **Cài bằng `git clone`** (không dùng ZIP/tải lẻ): để `git describe` chạy →
  `WEBUI_VERSION` đúng → service-worker cache tự bust mỗi lần deploy. Nếu buộc
  phải đóng gói không có `.git`, ghi `api/_version.py` với `__version__ = 'vX.Y.Z'`.

## Cài / chạy
```bash
git clone https://github.com/baquancoo-xorg/hermes-webui-nothingOS hermes-webui-ng
cd hermes-webui-ng
cp .env.example .env          # đặt HERMES_WEBUI_PASSWORD
python3 bootstrap.py          # tự tạo .venv (Python 3.11+) + dò engine
# mở http://127.0.0.1:8787
```

## Thay thế WebUI production (switch)
Giả định service hiện tại chạy qua systemd/`ctl.sh` tại một thư mục app.
1. **Backup state** (không nằm trong repo): `~/.hermes/webui` (session, settings).
   State giữ nguyên giữa các bản — không cần migrate.
2. Dừng service cũ: `systemctl --user stop hermes-webui` (hoặc `./ctl.sh stop`).
3. Trỏ service sang thư mục bản mới, hoặc cập nhật repo tại chỗ:
   ```bash
   git fetch origin && git checkout main && git pull --ff-only
   ```
4. Khởi động lại: `systemctl --user start hermes-webui` (hoặc `./ctl.sh start`).
5. Kiểm tra: `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8787/` = 200;
   mở trình duyệt, **hard reload** (Cmd/Ctrl+Shift+R) lần đầu để service worker
   nạp cache mới (tránh trang trắng do cache cũ thời v2).

## Phát hành & Cập nhật (Releasing & Updates)

WebUI **đã có sẵn** banner thông báo cập nhật trong app (nút **Update Now**). Nó so
HEAD đang chạy với **release tag mới nhất** dạng `vX.Y.Z-nothingos`. Banner chỉ im
lặng khi fork **chưa cắt tag mới** — nên "phát hành một bản" = "push một tag".

### Cắt một bản phát hành
```bash
scripts/release.sh 1.1.0                 # tạo + push tag v1.1.0-nothingos
scripts/release.sh 1.1.0 --gh-release    # kèm GitHub Release (auto changelog, cần gh)
scripts/release.sh 1.1.0 --dry-run       # chỉ in lệnh, không tạo tag
```
Script tự kiểm tra trước khi tag: đang ở `main`, tracked files sạch, `main` local ==
`origin/main`, version đúng định dạng `X.Y.Z`, và tag chưa tồn tại. Tag là annotated,
trỏ vào HEAD đã push. Version stamp (`WEBUI_VERSION`) lấy từ `git describe --tags` nên
tự cập nhật theo tag mới — không cần sửa code.

### Banner quyết định thế nào
- **Người cài đúng tag** (`git checkout vX.Y.Z-nothingos`): thấy banner khi có tag mới
  hơn → theo **bản ổn định**.
- **Người clone `main`** (HEAD đã vượt tag): updater tự chuyển sang so `origin/main` →
  thấy banner theo **từng commit** push lên main. Cả hai do engine xử lý tự động.

### "Update Now" làm gì
`git fetch` + `git pull --ff-only` tới ref đích, rồi server tự khởi động lại. Thay đổi
cục bộ được stash/restore; nếu lịch sử đã rẽ nhánh (diverged) thì pull fail an toàn và
hiện nút **Force update** (reset cứng về remote — sẽ mất commit local).

### ⚠️ Lưu ý Docker
Với bản chạy bằng **Docker image** dựng sẵn, "Update Now" chạy `git pull` *bên trong
container* và **không persist** sau khi container restart (image bất biến). Người dùng
Docker phải cập nhật bằng `docker pull` image mới / rebuild, không dùng nút trong app.
Updater không nhận biết Docker cho repo webui.

## Rollback
Bản cũ (Tungbillee + v2 SPA) được giữ ở nhánh `archive/tungbillee-nothingos`.
```bash
git checkout archive/tungbillee-nothingos
# hoặc về đúng commit reset nền:
# git checkout 9d8b8fd   # "reset base to nesquena master"
systemctl --user restart hermes-webui
```
Vì state ở `~/.hermes/webui` tách khỏi code, rollback không mất dữ liệu.

## Nếu gặp trang trắng (đã khử nguyên nhân, nhưng để phòng)
1. DevTools → Application → Service Workers → **Unregister** + Clear storage → reload.
2. Kiểm tra `curl http://HOST:8787/ | grep -c '__WEBUI_VERSION__'` = 0 (placeholder
   đã thay). Nếu khác 0 → server chưa serve đúng (kiểm tra Python ≥3.11).
3. Console (F12) → copy lỗi đỏ + tab Network → request `.js`/`.css` nào 404.

## Khác biệt so với upstream nesquena
- Skin: chỉ `nothingos` (đã xoá 16 skin). Theme: Light/Dark (bỏ System).
- Thêm: `agent_config.py`, `dash_cost.py`, `dash_roster.py`, `library.py` + routes.
- `bootstrap.py`: guard Python ≥3.11, dựng `.venv` qua `python -m venv --symlinks`.
- `sw.js`: precache thêm `tokens.css` + `os-widgets.js`.
