# `installer/` — Bộ cài Windows

**Owner:** D · **Bắt đầu:** cổng G1 (build thử) · **Trạng thái:** 🟢 đã có cấu hình, chờ build trên Windows

> ⚠️ Đây là **yêu cầu bắt buộc của đề bài** ("tạo bộ cài đặt") và là thứ dễ vỡ nhất.
> Build thử ngay G1, dù app còn trống.

## Chạy build

```bash
make build-installer        # = bash scripts/build_installer.sh
```

- macOS/Linux: ra `dist/CafeTLU/` (PyInstaller onedir), **không** ra `.exe` — Inno Setup chỉ có trên Windows.
- Windows: ra thêm `installer/Output/CafeTLU-Setup-v<version>.exe`.
- CI: `gh workflow run Release` → tải artifact `CafeTLU-Setup`; hoặc push tag `v*` để vào GitHub Release.

Version lấy từ `shared/version.py` → `scripts/build_installer.sh` truyền `/DMyAppVersion` cho ISCC
và sinh `build/version_info.txt` cho `.exe`. Không sửa version trong `.iss`/`.spec`.

## Đặt gì ở đây

| File | Việc |
|---|---|
| `cafetlu.spec` | PyInstaller: `datas`, `hiddenimports`, `excludes`. **Nguồn chân lý** về file nào được đóng gói |
| `cafetlu.iss` | Inno Setup: AppId, version, icon, shortcut, uninstaller |
| `app.ico` | Icon nhiều kích thước (16/32/48/256) |
| `Output/` | Kết quả build — **đã gitignore**, không commit |

## KHÔNG đặt

- `.exe` đã build (dùng GitHub Release để chia sẻ)
- `.env`, DB local, thư mục test trong bộ cài
- File font/thư viện có bản quyền

## Quy ước

Build **chạy trên GitHub Actions `windows-latest`** (`.github/workflows/release.yml`) — không cần
máy Windows. Kích hoạt: `git tag v1.0.0 && git push origin v1.0.0`.
Đọc skill `win-installer` trước khi sửa. Kiểm tra: cài trên **máy Windows sạch**, gỡ sạch.
