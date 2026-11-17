# Kết quả cài thử bộ cài CafeTLU trên Windows sạch

- Máy: `runnervmm7ud1` · Microsoft Windows Server 2025 Datacenter 10.0.26100
- Bộ cài: `CafeTLU-Setup-v0.1.0.exe` · 37.6 MB · SHA256 `A30303FBA378ED218C2C1ECFD6174F8292721C004E41A53F07335095AC1C5FD6`
- Lúc chạy: 2026-11-17 12:51:50 +00:00
- Kết quả: **13/13 bước đạt**

| Bước | Kết quả | Chi tiết |
|---|---|---|
| Có file bộ cài | PASS | CafeTLU-Setup-v0.1.0.exe · 37.6 MB · SHA256 A30303FBA378ED218C2C1ECFD6174F8292721C004E41A53F07335095AC1C5FD6 |
| Bộ cài đủ lớn (>20 MB, có payload PyInstaller) | PASS | 37.6 MB |
| Máy sạch trước khi cài | PASS | C:\CafeTLU-verify chưa tồn tại |
| Cài im lặng (/VERYSILENT) | PASS | exit code 0 sau 6 giây |
| Có CafeTLU.exe sau khi cài | PASS | C:\CafeTLU-verify\CafeTLU.exe |
| Có thư mục _internal (onedir) | PASS | C:\CafeTLU-verify\_internal |
| Có bộ gỡ cài đặt unins000.exe | PASS | C:\CafeTLU-verify\unins000.exe |
| Có shortcut trong Start Menu | PASS | tìm CafeTLU*.lnk |
| App khởi động và mở cửa sổ | PASS | pid 8056 · tiêu đề 'CafeTLU — Quản lý quán café' |
| Chụp ảnh cửa sổ (PrintWindow) | PASS | verification/gui.png · 27 KB |
| Tắt app không treo | PASS | đóng cửa sổ chính |
| Gỡ cài im lặng | PASS | exit code 0 |
| Gỡ sạch (không còn CafeTLU.exe) | PASS | C:\CafeTLU-verify\CafeTLU.exe |
