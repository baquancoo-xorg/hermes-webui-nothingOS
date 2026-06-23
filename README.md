# Hermes WebUI All-in-One

Giao diện web v2 (React) **gộp sẵn** vào backend Hermes WebUI — chạy **1 tiến trình duy nhất**,
không cần Node, không cần chạy 2 service. Vào thẳng `http://127.0.0.1:8787` là thấy UI v2.

> Bản này gộp `hermes-webui` (backend, MIT — nesquena/hermes-webui) + UI v2 (prebuilt).
> Backend tự phục vụ luôn UI v2 ở `/` và bỏ giao diện v1 cũ.

## Yêu cầu (BẮT BUỘC đọc)

Cần **engine `hermes-agent`** của NousResearch cài sẵn (bản này KHÔNG kèm engine 2.7GB).

- Engine phải nằm ở `~/.hermes/hermes-agent` (đường dẫn mặc định backend tự dò).
- ⚠️ **KHÔNG chạy `hermes dashboard`**: lệnh đó mở UI GỐC của NousResearch (port 9119), KHÁC hoàn toàn
  UI v2 này. Nếu thấy giao diện tên "HERMES AGENT" nền xanh quân đội → anh đang vào nhầm UI gốc.
- Bản này dùng engine chỉ như **thư viện** (`import hermes_cli`), không đụng vào engine.

## Cài đặt

```bash
# 1. Clone repo này
git clone <repo-url> hermes-allinone && cd hermes-allinone

# 2. Tạo file .env từ mẫu
cp .env.example .env
#    Mở .env, đặt HERMES_WEBUI_PASSWORD (mật khẩu đăng nhập).

# 3. Chạy (backend tự tạo venv + dò engine ~/.hermes/hermes-agent)
python3 bootstrap.py
```

## Dùng

Mở trình duyệt: **http://127.0.0.1:8787**

- Gõ địa chỉ gốc là tự vào UI v2 (không cần gõ `/v2`).
- Đăng nhập bằng mật khẩu đã đặt trong `.env`.
- Mọi tính năng: Chat, Workspaces, Profiles, Kanban, Dashboard, Skills, Memory, Tasks, Insights, Logs.

## Cổng

| Cổng | Là gì |
|------|-------|
| **8787** | UI v2 + API (bản này) — **vào cái này** |
| 9119 | `hermes dashboard` gốc NousResearch — KHÔNG dùng |

Đổi cổng: đặt `HERMES_WEBUI_PORT` trong `.env`.

## Khắc phục sự cố

- **Màn "Không kết nối backend"** → backend chưa chạy hoặc sai cổng. Kiểm tra `python3 bootstrap.py` còn chạy.
- **Vào ra giao diện xanh "HERMES AGENT"** → anh đang mở `hermes dashboard` (port 9119/khác), KHÔNG phải bản này. Mở đúng `http://127.0.0.1:8787`.
- **Lỗi `import hermes_cli`** → engine `hermes-agent` chưa cài ở `~/.hermes/hermes-agent`.

## Giấy phép

MIT. Dựa trên `nesquena/hermes-webui` (MIT) + `NousResearch/hermes-agent` (MIT). Giữ nguyên attribution gốc.
