# Bằng chứng cài thử bộ cài trên Windows sạch (cổng G1)

Cổng G1 đòi: **bộ cài cài được trên Windows sạch**, không chỉ build ra file `.exe`.
Cả nhóm dùng macOS (ADR-005) nên không ai cài thử bằng máy thật được. Cách làm: để
**GitHub Actions** cài thử trên runner `windows-latest` — mỗi lần chạy là một máy ảo Windows
**mới tinh**, không có Python, không có PySide6, không có bản cài cũ.

## Kết quả

| Hạng mục | Kết quả |
|---|---|
| Máy chạy | `runnervmm7ud1` · Microsoft Windows Server 2025 Datacenter 10.0.26100 |
| Bộ cài | `CafeTLU-Setup-v0.1.0.exe` · 37,6 MB · SHA256 `A30303FBA378ED218C2C1ECFD6174F8292721C004E41A53F07335095AC1C5FD6` |
| Cài im lặng `/VERYSILENT` | exit code 0 sau 6 giây |
| File sau khi cài | `CafeTLU.exe`, `_internal\`, `unins000.exe`, shortcut Start Menu |
| Chạy app | cửa sổ **CafeTLU — Quản lý quán café** hiện ra (pid 8056) |
| Gỡ cài | exit code 0, thư mục cài sạch, không còn `CafeTLU.exe` |
| Tổng | **13/13 bước đạt** |

- Ảnh cửa sổ app sau khi cài: [`gui-after-install.png`](gui-after-install.png) — chụp bằng
  `PrintWindow` (chụp đúng cửa sổ, không cần desktop hiển thị).
- Báo cáo đầy đủ 13 bước do CI sinh ra: [`ci-run-report.md`](ci-run-report.md).
- Lần chạy CI: <https://github.com/Haianh4705/cafe-tlu/actions/runs/44086760024> — mở lại được
  từng bước, log công khai.

## Chạy lại / tự kiểm chứng

```bash
gh workflow run release.yml --ref <nhánh>        # build + cài thử, tải artifact về
gh run download <run-id> -n install-verification-windows -D /tmp/verify
cat /tmp/verify/report.md
```

Hoặc tự chạy trên máy Windows bất kỳ:

```powershell
./scripts/verify_installer.ps1 -InstallerPath installer\Output\CafeTLU-Setup-v0.1.0.exe
```

Kịch bản nằm trong [`scripts/verify_installer.ps1`](../../../scripts/verify_installer.ps1);
job nằm trong [`.github/workflows/release.yml`](../../../.github/workflows/release.yml) (`verify-installer`).

## Giới hạn phải nói thật khi bảo vệ

- Runner **không có API và MySQL**, nên ảnh chỉ chứng minh **app cài được và mở lên được** (màn hình
  Đăng nhập). Luồng nghiệp vụ (đăng nhập → bán hàng → in hoá đơn) là việc của **G2**, kiểm bằng
  `docs/test-cases.md` trên máy có `make up`.
- Ảnh chụp là cửa sổ ứng dụng, không phải ảnh chụp toàn màn hình desktop — vì vậy không thấy được
  shortcut ngoài desktop; shortcut Start Menu được kiểm bằng bước `tìm CafeTLU*.lnk` (PASS).
- Bộ cài build lại mỗi lần nên SHA256 đổi theo; SHA ở trên là của lần chạy ghi trong
  `ci-run-report.md`, không phải SHA của file đang có trong Release `v0.1.0` (build ngày 09-11).
