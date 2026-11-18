# CafeTLU — Quản lý quán café TLU

[![CI trên develop](https://github.com/Haianh4705/cafe-tlu/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/Haianh4705/cafe-tlu/actions/workflows/ci.yml?query=branch%3Adevelop)

Ứng dụng desktop quản lý quán café, BTL Python 2026 (đề tài 5). Trên nhánh `develop`, nhân viên có thể đăng nhập và quản lý thực đơn theo quyền. Khách có thể tự chọn món, gửi đơn và nhận mã VietQR tại Kiosk.

[Xem yêu cầu đề bài](Danh-sach-BTL-hoc-phan-Python-TLU-2026.pdf) · [Xem tiến độ](https://github.com/Haianh4705/cafe-tlu/milestones)

## 1. Cài lần đầu

**Cần có** Python 3.12, Git, GNU Make và Docker Desktop đang chạy. Trên Windows, dùng Git Bash có GNU Make hoặc WSL có Docker tích hợp và hỗ trợ mở ứng dụng đồ hoạ.

Mở terminal và chạy lần lượt:

```bash
git clone --branch develop https://github.com/Haianh4705/cafe-tlu.git
cd cafe-tlu
make install
make start
```

- `make install` tạo môi trường Python `.venv`, cài thư viện và tạo `.env` từ mẫu nếu chưa có.
- `make start` bật MySQL, chờ API sẵn sàng rồi mở cửa sổ CafeTLU. MySQL tự nạp dữ liệu mẫu khi khởi tạo volume lần đầu.

### Thử ứng dụng

| Muốn thử | Thao tác |
|---|---|
| Quản lý thực đơn | Đăng nhập bằng tài khoản mẫu `admin` / `123456` rồi mở **Quản lý thực đơn**. Tài khoản này dành cho dữ liệu mẫu local. |
| Gọi món tại Kiosk | Chọn **Khách tự chọn món (Kiosk)** ở màn hình đăng nhập. Chọn bàn trống, thêm món và gửi đơn để xem mã QR. |
| Kiểm tra API | Mở [Swagger](http://127.0.0.1:8000/docs) hoặc [trạng thái API và MySQL](http://127.0.0.1:8000/health) khi ứng dụng đang chạy. |

## 2. Chạy hằng ngày và xử lý sự cố

Từ thư mục `cafe-tlu`, chạy `make start`. Đóng cửa sổ hoặc nhấn **Ctrl+C** để dừng ứng dụng và API. Chạy `make down` khi muốn tắt cả MySQL.

| Khi cần | Chạy hoặc kiểm tra |
|---|---|
| Kiểm tra máy khi khởi động lỗi | `make doctor`. Xem phiên bản Python, Docker, MySQL và cổng 3307. |
| MySQL chưa lên | Mở Docker Desktop, chạy `make up`. Dùng `make logs` để xem lỗi. |
| Cổng 3307 hoặc 8000 đang bận | Dừng dịch vụ đang dùng cổng đó hoặc đóng phiên CafeTLU đang chạy, rồi thử lại. |
| Debug từng thành phần | Chạy `make up`, mở `make api` ở một terminal và `make gui` ở terminal khác. |
| Xem cơ sở dữ liệu | Chạy `make tools`, mở [Adminer](http://localhost:8081) và dùng máy chủ `mysql`. |
| MySQL cũ thiếu bảng `refresh_tokens` | Làm theo [hướng dẫn nâng cấp DB](db/README.md). |
| Cần tạo lại toàn bộ dữ liệu mẫu | `make reset-db` **xoá toàn bộ dữ liệu MySQL local**. Chỉ dùng khi đã sao lưu hoặc dữ liệu có thể bỏ. |

Chạy `make help` để xem toàn bộ lệnh.

## 3. Nhận việc và gửi PR

1. Cài GitHub CLI (`gh`), chạy `gh auth login` rồi `make next` để xem Issue được giao. D có thể dùng `make next u=trungdunxg` để xem việc của thành viên khác.
2. Đọc tiêu chí nghiệm thu và phụ thuộc trong Issue. Tạo nhánh từ `develop` mới nhất theo [hướng dẫn đóng góp](CONTRIBUTING.md).
3. Chạy `make check` trước khi mở PR vào `develop`. Để chạy cả test MySQL, bật MySQL và dùng một database riêng đã tạo, có tên kết thúc bằng `_test`, ví dụ `DB_NAME=cafe_tlu_test make check`.
4. Ghi `Refs #<issue>`, kết quả kiểm tra, ba câu “Giải thích được” và cập nhật nhật ký cá nhân. Khi đủ checklist và CI xanh, squash merge vào `develop`, nghiệm thu rồi đóng Issue. Xem [quy tắc merge](WORKFLOW.md#32-quy-tắc-kiểm-tra-và-merge-pr).

| Thành viên | Mảng phụ trách chính | Nhật ký |
|---|---|---|
| A · [@bao20062005dh-creator](https://github.com/bao20062005dh-creator) | Luồng bán hàng: bàn, gọi món, thanh toán, hoá đơn và xác thực | [A](docs/log/A.md) |
| B · [@trungdunxg](https://github.com/trungdunxg) | Dữ liệu, KPI, báo cáo Excel/PDF, nhật ký thao tác và sao lưu MySQL | [B](docs/log/B.md) |
| C · [@MeoCamGuitar](https://github.com/MeoCamGuitar) | Giao diện PySide6, trải nghiệm đăng nhập và quản lý thực đơn | [C](docs/log/C.md) |
| D · [@Haianh4705](https://github.com/Haianh4705) | Điều phối, nghiệm thu, CI/CD, bộ cài, triển khai và bàn giao | [D](docs/log/D.md) |

Mỗi người có thể sửa các tầng cần thiết để hoàn thành Issue được giao. Xem người được gán và tiến độ thực tế trên [GitHub Issues](https://github.com/Haianh4705/cafe-tlu/issues?q=is%3Aissue+is%3Aopen) và [lộ trình G1–G6](docs/plan.md).

**Dùng AI trong repo:** yêu cầu agent đọc [AGENTS.md](AGENTS.md) và dùng skill [`next-task`](.claude/skills/next-task/SKILL.md) để xác định việc tiếp theo. [Danh sách skill theo loại việc](.claude/skills/README.md).

## 4. Xem mã nguồn và tài liệu

```text
PySide6 (gui/) → HTTP/JSON → FastAPI (api/) → SQLAlchemy → MySQL 8 (db/)
```

| Cần tìm | Đọc ở đâu |
|---|---|
| Mã giao diện, API và DB | [`gui/`](gui/), [`api/`](api/), [`db/`](db/) |
| Hợp đồng API và thiết kế dữ liệu | [API contract](docs/api-contract.md), [ERD](docs/erd.md), [quyết định kỹ thuật](docs/decisions.md) |
| Kiểm thử và câu hỏi bảo vệ | [`tests/`](tests/), [ca kiểm thử](docs/test-cases.md), [câu hỏi bảo vệ](docs/defense.md) |
| Hạ tầng, bộ cài và báo cáo | [`infra/`](infra/), [`installer/`](installer/), [`report/`](report/), [bản phát hành](https://github.com/Haianh4705/cafe-tlu/releases) |
| Quy trình và lịch sử thay đổi | [WORKFLOW.md](WORKFLOW.md), [luồng Issue → PR](docs/workflow.md), [CHANGELOG.md](CHANGELOG.md) |
