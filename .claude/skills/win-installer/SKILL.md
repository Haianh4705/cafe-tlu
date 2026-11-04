---
name: win-installer
description: Đóng gói CafeTLU thành bộ cài Windows (.exe) và sửa lỗi đóng gói. Dùng khi "build bộ cài", "app không mở trên máy khác", "PyInstaller lỗi thiếu module", "installer nặng/vỡ", hoặc ở cổng G1/G4/G6.
---

# Bộ cài Windows

## Sự thật quan trọng nhất

Đề bài **bắt buộc** có bộ cài. Đây là việc hay vỡ nhất và hay bị để tới tuần cuối.
**Build thử ngay tuần 1** dù app còn trống — nếu đường ống đóng gói không thông thì phải biết sớm.

Build chạy trên **GitHub Actions `windows-latest`** (không cần máy Windows, không cần VM).
Pipeline đã có sẵn: `.github/workflows/release.yml`, kích hoạt khi push tag `v*`.

## Cấu trúc

```
installer/
├── cafetlu.spec          # PyInstaller — nguồn chân lý về file nào được đóng gói
├── cafetlu.iss           # Inno Setup — bộ cài, shortcut, uninstall
├── app.ico               # icon (16/32/48/256 trong 1 file .ico)
└── Output/               # kết quả build (gitignore)
```

## `cafetlu.spec` — những dòng quyết định thành bại

```python
a = Analysis(
    ["gui/main.py"],
    pathex=[],
    datas=[
        ("assets", "assets"),  # ảnh món, icon, file .ui
        ("gui/styles", "gui/styles"),  # nếu tách QSS ra file
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "pymysql",
        "sqlalchemy.dialects.mysql",
        "passlib.handlers.bcrypt",
        "bcrypt",
    ],
    excludes=["tests", "pytest", "PySide6.QtWebEngineCore"],  # bỏ cho nhẹ
    noarchive=False,
)
```

- `--onedir` (mặc định trong spec) **tốt hơn** `--onefile` cho app Qt: khởi động nhanh,
  ít bị antivirus chặn, dễ debug.
- Mọi tài nguyên đọc lúc chạy **phải** đi qua `sys._MEIPASS` khi đã đóng gói:

```python
# shared/paths.py
def resource_path(rel: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / rel
```

- Nếu quên `hiddenimports`/`datas`, app chạy trên máy dev nhưng **chết im lặng** trên máy sạch.
  Đây là lỗi số 1.

## `cafetlu.iss` — checklist nội dung

- [ ] `AppId` cố định (đổi AppId = cài thành app khác, mất đường uninstall)
- [ ] `AppVersion` lấy từ **một nguồn duy nhất** (`shared/version.py`), không gõ tay lần 2
- [ ] Icon, License, `OutputBaseFilename=CafeTLU-Setup-v{version}`
- [ ] Shortcut Desktop + Start Menu
- [ ] `UninstallDisplayIcon`, và **xoá sạch** khi gỡ (không để lại trong `Program Files`)
- [ ] `PrivilegesRequired=lowest` nếu chỉ cài cho user (tránh cần admin)
- [ ] Không đóng gói `.env`, DB local, thư mục test

## Lỗi thường gặp và cách xử lý

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| Mở app không có gì xảy ra | Thiếu module/asset, exception bị chôn | Build bản console (`console=True`) để thấy traceback |
| `ModuleNotFoundError` trên máy sạch | Thiếu `hiddenimports` | Thêm module; test lại trên VM |
| Ảnh/icon không hiện | Đọc đường dẫn tương đối | Dùng `resource_path()` |
| App chậm 5–10s khi mở | `--onefile` giải nén mỗi lần | Chuyển `--onedir` |
| "Windows protected your PC" | Chưa ký số (bình thường với đồ án) | Ghi chú trong README + hướng dẫn "More info → Run anyway" |
| Không tìm thấy `docker`/`mysql` | Máy người dùng không có | App phải báo lỗi thân thiện + hướng dẫn cài, không crash |
| Lỗi font tiếng Việt | Font không có trên máy đích | Nhúng font vào `assets/fonts` + `QFontDatabase.addApplicationFont` |

## Quy trình phát hành

```bash
# 1. Chỉ khi develop đã qua G5
git switch -c release/v1.0.0
# 2. Bump shared/version.py  (một chỗ duy nhất)
# 3. PR vào main -> merge
git tag -a v1.0.0 -m "Bản nộp BTL"
git push origin v1.0.0        # CI tự build + đính vào GitHub Release
```

## Checklist trước khi coi là xong

- [ ] Cài được trên **máy Windows sạch** (chưa có Python, chưa có MySQL client)
- [ ] Mở app từ Start Menu **và** từ shortcut Desktop
- [ ] Đăng nhập + xem danh sách món chạy được (tức là API/DB path hoạt động)
- [ ] Gỡ cài đặt: không còn thư mục trong `Program Files`, không còn shortcut
- [ ] `AppVersion` hiển thị trong app khớp với tên file cài
- [ ] Dung lượng hợp lý (< 150MB) — nếu lớn hơn, kiểm tra `excludes`
- [ ] Ảnh chụp từng bước cài → `docs/screenshots/installer/`
