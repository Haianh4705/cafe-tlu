# Ôn bảo vệ — phần D (Hạ tầng · CI · Đóng gói · QA)

> Dùng kèm [`defense.md`](defense.md). File này trả lời: **thầy sẽ hỏi gì về phần mình, trả lời
> thế nào cho đúng, và chỉ tay vào đâu trong code.**
>
> Quy tắc duy nhất: **mọi câu trả lời phải chỉ được vào một dòng code hoặc một lần chạy thật.**
> Câu nào không chỉ được → chưa học, đừng nói.
>
> Nhật ký việc của tôi (bằng chứng commit/PR + AI đã làm gì): [`log/D.md`](log/D.md).

## 0. Cách dùng (30 phút trước buổi bảo vệ)

| Thời gian | Việc |
|---|---|
| 5 phút | Học thuộc **mục 1** (bài nói 90 giây) + **mục 9** (số liệu) |
| 15 phút | Đọc **mục 3–6**, mỗi mục tự nhẩm câu hỏi rồi che đáp án |
| 10 phút | Chạy **mục 10** (demo 5 phút) một lần trên máy mình |

Nếu chỉ còn 5 phút: đọc **mục 1**, **mục 2**, **mục 8**.

---

## 1. Bài nói 90 giây — "phần em làm gì"

> Nói theo thứ tự **vấn đề → cách làm → bằng chứng**, không kể lể.

"Em phụ trách hạ tầng, đường ống CI/CD, đóng gói và QA. Cụ thể bốn việc:

1. **Môi trường chạy giống nhau cho 4 máy** — MySQL 8.0 chạy bằng Docker Compose, cổng host **3307**
   để không đụng MySQL cài sẵn; một lệnh `make up` là có DB, `make doctor` kiểm được máy đã đủ
   điều kiện chưa (`docker-compose.yml`, `Makefile:38-54`).
2. **Backend đóng gói thành image** — `infra/Dockerfile`, chạy bằng user thường (không phải root),
   có `HEALTHCHECK` gọi `/health`, và `infra/docker-compose.prod.yml` không mở cổng DB ra ngoài.
3. **CI chặn code lỗi vào `develop`** — 2 job `Lint & format` và `Test`, test chạy với MySQL thật
   trong service container; nhánh `develop` bị khoá: phải 1 approval + 2 check xanh + linear history.
4. **Bộ cài Windows** — PyInstaller đóng GUI thành thư mục chạy được, Inno Setup bọc thành
   `CafeTLU-Setup-v0.1.0.exe`; vì cả nhóm dùng macOS nên **build trên `windows-latest` của GitHub
   Actions** khi push tag `v*`, đính thẳng vào GitHub Release (ADR-005).

Bằng chứng: PR **#47** (bộ cài), **#48** (doctor + compose production), **#46** (lộ trình theo cổng),
và Release `v0.1.0` có file `.exe` 39,4 MB tải được."

**Nếu thầy hỏi "em có tự làm không?"** → mở `git log --author=Haianh4705 --oneline` và PR #47, chỉ
từng dòng. Không nhận phần của A/B/C.

---

## 2. Ba câu "Giải thích được" — viết sẵn, dùng lại được

### PR #47 — bộ cài Windows

1. **Làm gì:** đóng GUI PySide6 thành `dist/CafeTLU/` bằng PyInstaller (`onedir`) rồi bọc thành một
   file cài `.exe` bằng Inno Setup, tự lấy version từ `shared/version.py`.
2. **Vì sao cách này:** `onedir` khởi động nhanh và ít bị antivirus chặn hơn `onefile` (mỗi lần chạy
   phải giải nén ra `%TEMP%`); tách 2 tầng PyInstaller/Inno để đổi installer không phải build lại Python.
3. **"Sao không dùng X?"** — "Dùng `onefile` được, nhưng đổi lại app chậm 3–10 giây mỗi lần mở và
   hay bị Defender cách ly; nhóm chọn `onedir` vì app phải mở–đóng liên tục trong giờ bán hàng."

### PR #48 — doctor + compose production

1. **Làm gì:** `make doctor` không chỉ hỏi "container có chạy không" mà đọc **trạng thái health** của
   `cafetlu-mysql` và mở thử socket tới `127.0.0.1:3307`; thêm khung `docker-compose.prod.yml`.
2. **Vì sao:** container `running` vẫn có thể chưa sẵn sàng nhận truy vấn — MySQL khởi tạo mất
   20–30 giây; kiểm health + cổng là kiểm đúng thứ mà `make api` cần.
3. **"Sao không dùng `docker compose ps`?"** — "`ps` chỉ in trạng thái, phải parse text; `docker inspect
   --format '{{.State.Health.Status}}'` trả đúng một chuỗi nên script `if` được, và không phụ thuộc
   phiên bản compose."

### PR #46 — lộ trình theo cổng

1. **Làm gì:** thay kế hoạch 8 tuần bằng 6 cổng **G1–G6**, mỗi cổng có điều kiện ra cổng đo được.
2. **Vì sao:** nhóm chạy không đều (A/B chậm, C nhanh) — lịch tuần tạo cảm giác "đúng tiến độ" dù
   chưa có `schema.sql`; cổng thì không thể "qua" khi thiếu điều kiện.
3. **"Sao không giữ lịch tuần cho dễ chấm?"** — "Vẫn có thứ tự và ước lượng giờ trong `docs/plan.md`;
   chỉ bỏ mốc tuần vì mốc đó không kiểm chứng được, còn cổng thì kiểm bằng lệnh."

---

## 3. Docker — kiến thức nền + áp vào repo

### 3.1 Khái niệm phải nói đúng

| Khái niệm | Nói gọn |
|---|---|
| Image vs container | Image là **khuôn chỉ đọc** (các lớp layer); container là **tiến trình đang chạy** từ image + một lớp ghi tạm |
| Layer & cache | Mỗi instruction trong Dockerfile tạo 1 layer; layer không đổi thì lấy từ cache. **Đổi thứ tự COPY là đổi cache** |
| Volume | Dữ liệu sống ngoài vòng đời container; `docker compose down` **không** mất, `down -v` mới mất |
| Port mapping | `"3307:3306"` = **host:container**. Trong container MySQL vẫn 3306 |
| Healthcheck | Lệnh chạy định kỳ trong container; trạng thái `starting → healthy / unhealthy`, khác hẳn "running" |
| `EXPOSE` | Chỉ là **tài liệu**, không mở cổng; mở thật là do `ports`/`-p` |

### 3.2 `infra/Dockerfile` — từng quyết định

```dockerfile
FROM python:3.12-slim                          # :11
RUN groupadd --system cafe && useradd …        # :20  user thường
COPY requirements.txt ./ ; RUN pip install …   # :22-23  cache layer
COPY api ./api ; COPY shared ./shared          # :25-26
RUN chown -R cafe:cafe /app ; USER cafe        # :28-29
EXPOSE 8000                                    # :31  chỉ là tài liệu
HEALTHCHECK … urlopen('…/health')              # :33-34
CMD ["uvicorn","api.main:app","--host","0.0.0.0","--port","8000"]  # :36
```

- **`slim` không dùng `alpine`:** alpine dùng musl libc → nhiều wheel phải biên dịch lại, chậm và dễ
  lỗi; `slim` (Debian) ~150 MB, wheel manylinux dùng thẳng.
- **COPY `requirements.txt` trước, code sau:** sửa code không làm mất cache bước `pip install`
  (bước nặng nhất). Đây là câu trả lời chuẩn cho "làm sao build nhanh?".
- **`PYTHONUNBUFFERED=1`:** không có nó, log của uvicorn bị buffer → `docker logs` trống, khó debug.
  **`PYTHONDONTWRITEBYTECODE=1`:** không sinh `__pycache__` rác trong image.
- **`useradd --system cafe` + `USER cafe`:** mặc định container chạy **root**; nếu app bị khai thác
  (RCE) thì kẻ tấn công có root trong container, kết hợp lỗi kernel là leo thang ra host. Chạy user
  thường là giảm thiệt hại, không phải "cho đẹp".
- **HEALTHCHECK dùng `python -c "urllib.request…"`:** image `slim` **không có `curl`**; dùng chính
  Python có sẵn, không phải `apt-get install curl` (thêm ~10 MB + 1 layer).
- **`--host 0.0.0.0`:** trong container, `127.0.0.1` chỉ nghe trong namespace của container → publish
  ra ngoài không tới được.
- **`COPY api` + `COPY shared`:** `shared/version.py` là nguồn version duy nhất nên API cũng cần nó.

> ⚠️ **Chỗ yếu phải nói thật:** image hiện **1,37 GB** vì `requirements.txt` dùng chung có **PySide6**
> (thư viện GUI, ~1 GB) trong khi server không cần. G4 sẽ tách `requirements-api.txt`. Nói trước khi
> bị hỏi = điểm cộng; giấu rồi bị bắt = mất điểm.

### 3.3 `docker-compose.yml` (dev)

| Dòng | Nội dung | Vì sao |
|---|---|---|
| `:25-27` | `"${DB_PORT:-3307}:3306"` | 3307 tránh đụng MySQL cài sẵn (ADR-004); `:-` = giá trị mặc định khi `.env` không có |
| `:22-24` | `--character-set-server=utf8mb4` | Tiếng Việt + emoji; `utf8` (3 byte) **không** lưu được emoji |
| `:34-41` | healthcheck `mysqladmin ping` | MySQL "running" vẫn chưa nhận truy vấn; ping dùng đúng user/pass nên kiểm cả auth |
| `:28-29` | `volumes: cafetlu_mysql_data` | `make down` rồi `make up` vẫn còn dữ liệu; `make reset-db` = `down -v` mới xoá |
| `:48` | `profiles: ["tools"]` | Adminer không chạy mặc định, chỉ `make tools` mới bật → nhẹ máy |
| `:49-51` | `depends_on: condition: service_healthy` | Adminer đợi MySQL healthy, không lỗi "can't connect" khi vừa bật |
| `:15` | `container_name: cafetlu-mysql` | Tên cố định để `make doctor` inspect được (compose mặc định đặt `cafetlu-mysql-1`) |

### 3.4 `infra/docker-compose.prod.yml` — khác dev ở đâu

- **Không publish cổng MySQL** → DB chỉ nằm trong network nội bộ của compose. Đây là câu trả lời cho
  "sao DB không bị quét từ Internet".
- Biến dùng `${VAR:?message}` → thiếu biến là compose **dừng ngay** kèm lý do, không âm thầm chạy
  bằng mật khẩu mặc định. (`:-` = mặc định; `:?` = bắt buộc.)
- `restart: unless-stopped`, api build từ `infra/Dockerfile`, không mount source code.
- Kiểm chứng đã làm: `docker compose -f infra/docker-compose.prod.yml config` (có đặt biến môi
  trường) — validate cú pháp mà không cần chạy. Thiếu `MYSQL_ROOT_PASSWORD`/`JWT_SECRET` thì compose
  dừng kèm thông báo `thiếu trong .env.prod`; đó chính là hành vi mong muốn.

### 3.5 Câu hỏi hay gặp về Docker

| Câu hỏi | Trả lời |
|---|---|
| "Docker khác máy ảo thế nào?" | VM ảo hoá phần cứng, mỗi VM có kernel riêng, nặng GB và chậm khởi động; container chia sẻ kernel host, chỉ đóng gói tiến trình + thư viện, chạy trong vài giây |
| "Vì sao không cài MySQL trực tiếp?" | 4 máy 2 hệ điều hành, phiên bản lệch nhau, gỡ cài đặt để lại service; Docker cho mọi người **cùng một** MySQL 8.0 và xoá sạch bằng 1 lệnh (ADR-004) |
| "Vì sao cổng 3307?" | Máy nào cũng có thể đã có MySQL ở 3306 → đổi host port, container vẫn 3306, không sửa code |
| "Mất Docker thì sao?" | `.env` + `db/schema.sql` + `db/seed.sql` là đủ dựng lại; nhưng hiện schema/seed chưa có (#17/#18 của B) → rủi ro đang mở |
| "Sao không dùng Kubernetes?" | Bài 4 người, 1 máy chủ; K8s là chi phí vận hành không đổi lại được gì ở quy mô này (ghi trong ADR/plan) |

---

## 4. CI/CD và bảo vệ nhánh

### 4.1 `.github/workflows/ci.yml`

| Thành phần | Ở đâu | Giải thích |
|---|---|---|
| Trigger | `:6-10` | mọi `pull_request`, push vào `main`/`develop`, và bấm tay `workflow_dispatch` |
| `concurrency` + `cancel-in-progress` | `:12-14` | push 3 lần liên tiếp thì run cũ bị huỷ, không đốt phút CI |
| Job `lint` | `:21-42` | `ruff check` (lỗi logic/biến thừa/import sai) + `black --check` (format) |
| Job `test` | `:45-112` | pytest + coverage, chạy với **MySQL thật** trong `services` |
| `services.mysql` | `:49-61` | GitHub dựng container MySQL 8.0, chờ `health-cmd` trước khi chạy step |
| `QT_QPA_PLATFORM: offscreen` | `:71` | runner không có màn hình; Qt cần platform plugin, `offscreen` cho phép dựng widget mà không cần X11 |
| `apt-get … libegl1 libgl1 …` | `:87-92` | PySide6 cần `libEGL.so.1`; thiếu → pytest chết `INTERNALERROR` chứ không phải test fail (đã từng xảy ra) |
| `pytest -q --cov` | `:106` | coverage lấy cấu hình `[tool.coverage]` trong `pyproject.toml` |
| xử lý exit code 5 | `:108-111` | pytest trả 5 = "không có test nào"; giai đoạn đầu coi là đạt để ống không đỏ giả. **Hiện đã có 15 test → nhánh này không còn chạy** |

**Vì sao 2 job riêng, không gộp 1?** Chạy song song → thấy ngay "lỗi format" hay "lỗi logic"; và
branch protection bắt buộc đúng 2 tên check `Lint & format`, `Test`.

**Vì sao test cần MySQL thật?** Test chỉ mock DB sẽ xanh dù câu SQL sai; service container cho ta
đúng phiên bản 8.0 như máy dev, và bắt được lỗi kiểu `utf8mb4`, timezone, FK.

### 4.2 Bảo vệ nhánh (cấu hình thật, kiểm bằng `gh api`)

| Thiết lập | Giá trị | Vì sao |
|---|---|---|
| Required approvals | **1** | GitHub **không cho tự approve** PR của mình; nếu bắt 2 thì nhóm 4 người phải chờ 2 người, chậm |
| Required checks | `Lint & format`, `Test` | Chỉ chặn khi 2 job này xanh |
| Strict / up-to-date | bật | PR phải rebase lên `develop` mới nhất rồi mới merge → tránh "xanh trên code cũ" |
| Linear history | bật | Cấm merge commit; lịch sử 1 dòng, `git log` đọc được, revert dễ |
| `enforce_admins` | **tắt** | Chủ repo là admin; tắt để còn đường `gh pr merge --admin` khi bị kẹt vì không ai review |
| Code owner review | **không bật** | Mỗi người là owner duy nhất vùng mình → PR của A chỉ @A duyệt được → kẹt vĩnh viễn (ghi rõ trong `.github/CODEOWNERS`) |

**Câu bẫy: "Vậy bảo vệ nhánh có tác dụng gì khi em tự merge bằng `--admin`?"**
→ Trả lời thật: "Với người khác thì chặn đúng; với em là lỗ hổng có chủ ý. Em dùng `--admin` chỉ khi
PR của chính em mà không ai online, và luôn ghi lý do trong PR. Cách sửa đúng là bật `enforce_admins`
khi nhóm đủ người trực review — em đã ghi việc này trong `docs/setup-github.md`."

### 4.3 `.github/workflows/release.yml`

- `runs-on: windows-latest` — **điểm mấu chốt**: cả nhóm dùng macOS vẫn ra `.exe` (ADR-005).
- Bước `probe` (`:26-34`): chưa có `installer/*.iss` thì bỏ qua, ống không đỏ — cho phép merge cấu
  hình trước khi có app.
- Pin `pyinstaller==6.11.1` (`:55`): bản mới có thể đổi format spec → build vỡ lúc nộp bài.
- `upload-artifact@v4` (`:72`): tải `.exe` ở tab Actions dù chưa phải release.
- `softprops/action-gh-release@v3` (`:79-83`) + `permissions: contents: write` (`:16-17`): chỉ khi
  push tag `v*` mới tạo Release và đính file.
- Bài học thật đã gặp: Git Bash (MSYS) tự đổi `/DMyAppVersion=0.1.0` thành đường dẫn Windows → ISCC
  báo "more than one script filename"; sửa bằng `MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*"`
  (`scripts/build_installer.sh:100`). **Kể được lỗi này là điểm cộng** — nó chứng minh có chạy thật.

---

## 5. Đóng gói ứng dụng desktop

### 5.1 PyInstaller — `installer/cafetlu.spec`

Chuỗi 4 bước (nói đúng thứ tự khi bị hỏi):

```
Analysis  → quét import từ gui/main.py, gom module + DLL + data
PYZ       → nén bytecode thành 1 archive
EXE       → bootloader .exe (đọc PYZ, khởi động Python nhúng)
COLLECT   → gom tất cả vào dist/CafeTLU/ (+ _internal/)
```

| Dòng | Nội dung | Giải thích |
|---|---|---|
| `:20` | `exec(shared/version.py)` | Version **một nguồn**; `.spec` không ghi tay số nào |
| `:32` | `datas=[(assets, "assets")]` | File **không phải** module (font, ảnh) phải khai báo, nếu không app chết trên máy sạch |
| `:33-38` | `hiddenimports` QtCore/Gui/Widgets/**Svg** | Import kiểu động (`importlib`, plugin loader) mà phân tích tĩnh không thấy → phải khai; `QtSvg` cho icon `.svg` |
| `:43` | `excludes` tests/pytest/WebEngine/3DCore | Không kéo thứ không dùng; WebEngine một mình đã hàng trăm MB |
| `:59` | `console=False` | Bản phát hành không mở cửa sổ đen; khi debug đổi `True` để thấy traceback |
| `:65-66` | `icon`/`version` chỉ khi `sys.platform == "win32"` | Build trên macOS không lỗi vì thiếu file `.ico`/resource Windows |
| `:69-76` | `COLLECT` (onedir) | Ra **thư mục**, không phải 1 file |

**"Vì sao `onedir` không `onefile`?"** — 3 lý do, nói đúng 3:
1. `onefile` giải nén toàn bộ ra `%TEMP%` **mỗi lần chạy** → chậm 3–10 giây (app mở/đóng liên tục).
2. File `.exe` nén dễ bị Windows Defender/antivirus cách ly hoặc quét chậm.
3. Thiếu file thì `onedir` thấy ngay trong thư mục; `onefile` chỉ hiện "app crashed".

**"App đọc ảnh/font thế nào khi đã đóng gói?"** — `shared/paths.py:7-16`: nếu có `sys._MEIPASS`
(chế độ frozen) thì base là thư mục đó, ngược lại là gốc repo. `gui/main.py:286` gọi
`resource_path("assets/fonts/Manrope[wght].ttf")`. Với `onedir` PyInstaller 6, `_MEIPASS` trỏ vào
thư mục `_internal` — nơi `datas` được chép vào.

**"Sao `.spec` lại nằm trong repo?"** — `.gitignore` có `*.spec` nhưng có ngoại lệ
`!installer/cafetlu.spec`: spec là **cấu hình build**, mất là mất khả năng tái lập.

### 5.2 Inno Setup — `installer/cafetlu.iss`

| Dòng | Nội dung | Giải thích |
|---|---|---|
| `:21` | `AppId={{cd150c56-…}` | **Cố định** — Windows dùng để nhận diện "cùng một app"; đổi là thành app khác, cài chồng 2 bản, mất đường gỡ cũ |
| `:28` | `PrivilegesRequired=lowest` | Cài per-user, **không cần admin** — máy phòng lab bị khoá quyền |
| `:30` | `{autopf}` | Tự chọn `Program Files` (có quyền admin) hoặc `%LocalAppData%\Programs` (không admin) |
| `:34` | `OutputBaseFilename=CafeTLU-Setup-v{#MyAppVersion}` | Tên file có version → không ghi đè bản cũ, dễ đối chiếu Release |
| `:37-38` | `lzma2` + `SolidCompression` | 134 MB → **39,4 MB** |
| `:40-41` | `ArchitecturesAllowed=x64compatible` | Chặn cài trên Windows 32-bit (app đóng gói x64) |
| `:51` | `Source: ..\dist\CafeTLU\*` + `recursesubdirs` | Chép **nguyên** thư mục `onedir`, kể cả `_internal` |
| `:61-63` | `[UninstallDelete] {app}\logs` | Chỉ xoá file app sinh ra; **dữ liệu thật ở MySQL**, không đụng |
| `:15-17` | `#ifndef MyAppVersion` → `"0.0.0"` | Build tay không truyền `/D` vẫn không lỗi cú pháp |

**"Version đi từ đâu tới đâu?"** — `shared/version.py` → `scripts/build_installer.sh:26` đọc bằng
`python -c` → (a) sinh `build/version_info.txt` cho **Properties → Details** của `.exe`,
(b) truyền `/DMyAppVersion=$VERSION` cho ISCC → tên file cài. Một nguồn, ba chỗ dùng, không sửa tay.

**"Làm sao chắc app chạy trên máy người khác?"** — TC-PKG-01: máy Windows **sạch** (chưa Python,
chưa MySQL), cài bằng `Setup.exe`, mở từ Start Menu. ⚠️ **Hiện chưa làm** — đây là việc còn mở của
#26; phải nói thật và nêu kế hoạch (nhờ máy Windows/VM, chụp ảnh vào `docs/screenshots/installer/`).

### 5.3 Câu hỏi hay gặp về đóng gói

| Câu hỏi | Trả lời |
|---|---|
| "Sao không gửi source cho người dùng chạy `python main.py`?" | Người dùng quán café không cài Python/pip; bộ cài là yêu cầu bắt buộc của đề bài |
| "App cần backend, bộ cài có kèm backend không?" | Không. Bộ cài chỉ là **client**; backend chạy riêng (G4 deploy). Đây là hệ quả của ADR-006 (GUI không nối DB) |
| "Cài xong app không kết nối được API thì sao?" | Hiện báo lỗi kết nối, không treo (TC-PKG-04, phần C) — điểm yếu: chưa có màn hình cấu hình URL API |
| "Có ký số (code signing) không?" | Chưa — chứng chỉ tốn tiền; hệ quả: SmartScreen cảnh báo "Unknown publisher" lần đầu. Nói trước |
| "Update thế nào?" | Chưa có auto-update (TC-PKG-03 đang mở); hiện tải bản mới từ Release, `AppId` giữ nguyên nên cài đè được |

---

## 6. QA và quy trình (phần D còn lại)

### 6.1 Vì sao theo cổng, không theo tuần

- Cổng = **điều kiện kiểm chứng được** ("4/4 máy `make doctor` xanh", "DB có 50 món"), tuần = **thời
  gian trôi** — tuần 3 vẫn "đúng tiến độ" dù chưa có `schema.sql`.
- Thứ tự công việc không đổi, chỉ bỏ mốc lịch; ước lượng giờ vẫn giữ trong `docs/plan.md`.
- Có **đường găng**: `db/schema.sql` (B) chặn A (models) và C (màn hình) → giao B trước.

### 6.2 WIP limit và "đang chờ người khác thì làm gì"

- Mỗi người tối đa **2 việc** đang làm; hết mới nhận thêm (tránh 4 việc dở dang).
- Chờ người khác → làm việc không phụ thuộc: viết test, viết tài liệu, chụp ảnh, dọn CI. Có mục riêng
  trong `docs/plan.md` mục 10.

### 6.3 `docs/test-cases.md` — nói đúng con số

- **24 ca** thiết kế, chia 6 nhóm; cột "Người" ghi ai viết, ai kiểm chứng lại.
- Quy ước: **`PASS` chỉ khi chạy end-to-end với API + MySQL thật**. Unit test mock **không** được
  tính là PASS.
- Hiện tại: **0 ca PASS end-to-end**; **15 unit test tự động** xanh trên `develop` (22 nếu tính nhánh
  C đang mở). Trả lời đúng như vậy, đừng nói "đã test hết".
- Đã bắt được lỗi: C đánh `PASS` cho TC-ORD-01/03 khi chưa có API/DB → em review, yêu cầu trả về `⬜`.
  **Đây là ví dụ tốt để kể** khi thầy hỏi "QA làm gì".

### 6.4 Định nghĩa "xong" (Definition of Done)

`make lint` + `make test` xanh (dán kết quả thật) · đúng phạm vi Issue · có test cho hành vi mới ·
CHANGELOG 1 dòng · ảnh chụp nếu là UI · **3 câu "Giải thích được"** · commit Conventional Commits.

---

## 7. Đáp án 10 câu trong `defense.md` mục D

> Nói 2–4 câu mỗi câu, tay chỉ vào file. Đây là bản trả lời mẫu, học ý không học chữ.

1. **Docker là gì? Vì sao dùng cho MySQL?**
   Docker đóng gói tiến trình + thư viện thành image, chạy bằng container chia sẻ kernel host. MySQL
   chạy trong container nên 4 máy (macOS/Windows) dùng **đúng** MySQL 8.0, cùng charset, cùng
   timezone; xoá sạch bằng `make reset-db` thay vì gỡ service trên từng máy. Xem `docker-compose.yml`.

2. **Vì sao cổng 3307 không 3306?**
   Nhiều máy đã có MySQL cài sẵn ở 3306 → đụng cổng, khó biết app nối vào DB nào. Đổi **host port**
   sang 3307, container vẫn 3306 nên code không phải sửa. ADR-004.

3. **`hiddenimports` để làm gì?**
   PyInstaller dò import bằng phân tích tĩnh; import động hoặc module do plugin nạp lúc chạy sẽ bị bỏ
   sót → app chết `ModuleNotFoundError` chỉ trên máy đã đóng gói. Khai trong `hiddenimports` là bảo
   nó "chép thêm mấy module này". `installer/cafetlu.spec:33`.

4. **Vì sao `--onedir` không `--onefile`?**
   `onefile` giải nén ra `%TEMP%` mỗi lần chạy (chậm 3–10 s) và dễ bị antivirus cách ly; `onedir`
   khởi động nhanh, thiếu file thì thấy ngay. Đổi lại: thư mục cài nhiều file hơn — Inno Setup lo
   phần đó.

5. **App đọc ảnh thế nào khi đã đóng gói?**
   Ảnh/font khai trong `datas` của spec, được chép vào `_internal/assets`. `shared/paths.py` kiểm
   `sys._MEIPASS` để biết đang chạy frozen hay dev rồi ghép đường dẫn; `gui/main.py:286` dùng nó để
   nạp font Manrope.

6. **CI làm gì? Mấy job? Khi nào chạy?**
   Hai job: `Lint & format` (ruff + black) và `Test` (pytest + coverage, MySQL 8.0 trong service
   container). Chạy mọi PR, mọi push vào `main`/`develop`, và bấm tay. Hai check này là điều kiện bắt
   buộc để merge vào `develop`.

7. **Làm sao build `.exe` khi cả nhóm dùng macOS?**
   Đẩy tag `v*` → `release.yml` chạy trên `windows-latest`: cài requirements + PyInstaller 6.11.1 →
   `scripts/build_installer.sh` → Inno Setup → upload artifact và đính vào Release. Không cần máy
   Windows (ADR-005).

8. **Đã chạy bao nhiêu test case, pass bao nhiêu?**
   24 ca thiết kế; **0 ca PASS end-to-end** vì API/DB chưa xong; **15 unit test** tự động xanh
   (`make test`). Nói rõ sự khác nhau giữa "unit test xanh" và "ca kiểm thử PASS".

9. **Làm sao chắc app chạy trên máy người khác?**
   Bằng chứng phải là **máy sạch**: Windows chưa Python/MySQL, cài `Setup.exe`, mở từ Start Menu
   (TC-PKG-01), rồi gỡ và kiểm không sót file (TC-PKG-02). Hiện **chưa chạy** — đang mở ở #26; đây là
   việc phải xong trước G3.

10. **Deploy thế nào, bảo mật ra sao?**
    Khung: `infra/Dockerfile` + `docker-compose.prod.yml` (API + MySQL, **không** publish cổng DB),
    biến môi trường `${VAR:?}` bắt buộc, chạy non-root, `HEALTHCHECK`. Trước khi deploy thật: `pip-audit`
    sạch, `JWT_SECRET` sinh mới, DB user **không phải root**, HTTPS qua reverse proxy. Deploy thật là
    G4 — chưa làm, đừng nói đã làm.

---

## 8. Câu bẫy và giới hạn phải thừa nhận

| Câu bẫy | Cách trả lời |
|---|---|
| "Image 1,4 GB, em tối ưu kiểu gì?" | Thừa nhận ngay: do `requirements.txt` dùng chung kéo PySide6; kế hoạch G4 tách `requirements-api.txt` + multi-stage; ước còn < 300 MB |
| "CI chỉ chạy trên Ubuntu, sao biết app chạy Windows?" | Đúng — CI chỉ build installer trên Windows, **không chạy test** ở đó. Bù lại bằng TC-PKG-01 trên máy sạch; đây là lỗ hổng đã biết |
| "Bảo vệ nhánh mà em vẫn `--admin` merge?" | Thừa nhận là lỗ hổng có chủ ý, chỉ dùng khi không ai review được, có ghi lý do; bật `enforce_admins` khi nhóm trực review đủ |
| "Test của nhóm có bao nhiêu % coverage?" | Nói số thật từ `make test` (15 test, coverage hiện thấp vì API chưa có); không bịa |
| "Sao không có test cho Dockerfile/installer?" | Đúng, chưa có test tự động cho hạ tầng; kiểm bằng tay theo TC-PKG. Ghi vào phần "hạn chế" của báo cáo |
| "Nếu push tag sai thì sao?" | Xoá tag local + remote, sửa version trong `shared/version.py` rồi tag lại; Release cũ phải xoá tay vì pipeline không tự dọn |
| "Dòng này làm gì?" (trỏ bất kỳ) | Nếu là file của mình: đọc được từng dòng — lý do tồn tại của `scripts/build_installer.sh`. Nếu là file của người khác: "phần này của A/C, em hiểu ở mức giao diện gọi API" — không đoán bừa |
| "Em copy ở đâu?" | Mở `git log --author=Haianh4705`, PR #47/#48/#46; chỉ phần tự viết, giải thích từng quyết định. Không có đoạn nào không giải thích được |

**Ba câu KHÔNG được nói:** "em đã test rồi" (khi chưa dán kết quả) · "cái này AI viết" (không phải
cách trả lời) · "phần này em không biết" (thay bằng: "phần này của X, em biết nó nhận/gửi gì").

---

## 9. Số liệu phải nhớ

| Số | Giá trị | Lấy ở đâu |
|---|---|---|
| Python | 3.12 (CI) · 3.12.13 (venv máy em) | `pyproject.toml`, `.python-version`, `.venv/bin/python -V` |
| MySQL | 8.0, host port **3307** | `docker-compose.yml:14,27` |
| API port | 8000 | `infra/Dockerfile:31`, `Makefile` |
| Job CI | 2 (`Lint & format`, `Test`) | `.github/workflows/ci.yml` |
| Test tự động | **15** trên `develop` (22 ở nhánh C đang mở) | `pytest --collect-only` |
| Ca kiểm thử thiết kế | **24**, PASS end-to-end **0** | `docs/test-cases.md` |
| Bộ cài | `CafeTLU-Setup-v0.1.0.exe`, **39,4 MB** | Release `v0.1.0` |
| `dist/CafeTLU` | 134 MB (Windows CI) / 116 MB (macOS) | log build |
| Image backend | **1,37 GB** (chưa tối ưu) | `docker images` |
| Bản cài bắt buộc | Inno Setup 6, PyInstaller **6.11.1** | `release.yml:55` |
| Cổng hiện tại | **G1** (chưa ra cổng) | `docs/plan.md` |

---

## 10. Demo 5 phút (thứ tự nên chạy)

| Bước | Lệnh | Nói gì khi nó chạy |
|---|---|---|
| 1 | `make doctor` | "Mỗi dòng là một điều kiện; mysql healthy + cổng 3307 mở là 2 dòng em thêm ở #48" |
| 2 | `git log --oneline -8` | "Lịch sử 1 dòng nhờ linear history; commit theo Conventional Commits" |
| 3 | `gh pr checks 47` hoặc mở tab Actions | "2 check bắt buộc, xanh mới merge được" |
| 4 | `gh release view v0.1.0` | "`.exe` 39,4 MB, build trên windows-latest, không cần máy Windows" |
| 5 | `make test` | "15 test, chạy cả trên máy em và trên CI" |

Nếu mạng/Docker hỏng: **không sửa live**, chuyển sang ảnh chụp trong `docs/screenshots/` và nói
"em có bằng chứng chạy thật ở đây". Bình tĩnh quan trọng hơn chạy được.

---

## 11. Từ điển nhanh (nói đúng tên)

| Việt | Anh / thuật ngữ |
|---|---|
| Ảnh (khuôn) / thùng chứa | image / container |
| Lớp | layer · bộ nhớ đệm build: build cache |
| Ổ đĩa ảo giữ dữ liệu | volume |
| Ghim cổng | port mapping / publish |
| Kiểm tra sức khoẻ | healthcheck |
| Đường ống | pipeline / workflow |
| Việc chạy | job · bước: step · ma trận: matrix |
| Chặn merge | required status checks / branch protection |
| Lịch sử thẳng | linear history |
| Đóng gói | packaging / freeze (PyInstaller) |
| Bộ cài | installer (Inno Setup) |
| Gỡ cài đặt | uninstaller |

---

## 12. Checklist trước buổi bảo vệ

- [ ] Nói 90 giây mục 1 không cần đọc giấy
- [ ] Trả lời được **10/10** câu mục 7, mỗi câu chỉ được vào file
- [ ] Thuộc **6 số** đầu tiên ở mục 9
- [ ] Chuẩn bị sẵn câu thừa nhận cho **4 chỗ yếu**: image 1,4 GB · CI không test Windows · chưa cài
      thử máy sạch · bảo vệ nhánh không enforce admin
- [ ] Trả lời được **≥ 5 câu** vùng khác (dùng `defense.md` mục A/B/C): kiến trúc GUI→API→DB,
      envelope `data/meta/error`, transaction khi tạo đơn, bcrypt/JWT, vì sao bảng chi tiết đơn lưu giá
- [ ] Chạy lại mục 10 một lần, chụp màn hình kết quả để dự phòng

---

## 13. Phụ lục — 5 câu vùng khác (mỗi câu 1–2 câu trả lời)

> `defense.md` yêu cầu mỗi người trả lời được ≥ 5 câu vùng người khác. Đây là bản ngắn.
> ⚠️ `api/` hiện **chưa có code** (#19–#22 của A), nên trả lời theo **thiết kế đã chốt** trong
> `docs/api-contract.md` + `docs/erd.md` và nói rõ "theo thiết kế", đừng nói "đã chạy".

| Câu | Trả lời ngắn |
|---|---|
| Kiến trúc tổng thể? Vì sao GUI không nối thẳng MySQL? | `gui/` → HTTP → `api/routers` → `api/services` → `api/models` → MySQL. Một chiều phụ thuộc. GUI không nối DB vì: đổi 1 chỗ áp cho mọi client, kiểm quyền ở server (client sửa được), và deploy/QR order sau này không phải viết lại (ADR-006) |
| Vì sao response bọc `data`/`meta`/`error`? | Để client có **một** hình dạng để xử lý: thành công thì `data` (+ `meta` cho phân trang), lỗi thì `error.code` + `message`. GUI rẽ nhánh theo `error.code` chứ không đoán theo HTTP status, nên thông báo tiếng Việt thống nhất |
| Tạo đơn mà lỗi giữa chừng thì sao? | Cả cụm (insert đơn + insert chi tiết + đổi trạng thái bàn) nằm trong **một transaction**; lỗi ở bước nào thì rollback, DB không có đơn nửa vời hay bàn bị khoá mà không có đơn |
| Sửa giá món thì hoá đơn cũ hiển thị giá nào? | Hoá đơn cũ giữ **giá tại thời điểm bán** — bảng chi tiết đơn lưu cột giá riêng, không join giá hiện tại của `products`. Đây chính là lý do phải có cột giá trong bảng chi tiết (câu B-2; tên cột do B chốt trong `docs/erd.md`) |
| Mật khẩu lưu thế nào? 401 khác 403 ở đâu? | Mật khẩu hash **bcrypt** cost ≥ 12 (`WORKFLOW.md:665`) — có salt, cố tình chậm; không plaintext, không mã hoá 2 chiều. 401 = chưa xác thực (thiếu/sai token), 403 = đã xác thực nhưng **không đủ quyền**; quyền kiểm ở server bằng `require_role`, ẩn nút trên GUI chỉ là UX (TC-AUTH-04 do em kiểm) |
