# ============================================================
# Makefile — một lệnh chuẩn cho cả nhóm. Xem WORKFLOW.md mục 18.5.
# Chạy `make` để xem danh sách lệnh.
#
# Windows: dùng Git Bash / WSL để có `make`.
#          (hoặc chạy trực tiếp lệnh trong README.md)
# ============================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help

# Ưu tiên python trong venv; nếu chưa có venv thì tìm python3.12 rồi mới tới python3.
PY := $(if $(wildcard .venv/bin/python),.venv/bin/python,$(shell command -v python3.12 2>/dev/null || echo python3))

.PHONY: help doctor install up down reset-db logs tools api gui test lint fmt check build-installer clean

# ------------------------------------------------------------
# Trợ giúp
# ------------------------------------------------------------
help: ## Hiện danh sách lệnh
	@echo ""
	@echo "  CafeTLU — lệnh phát triển"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	    | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'
	@echo ""

doctor: ## Kiểm tra môi trường máy (python, docker, git, .env)
	@echo "── Kiểm tra môi trường ────────────────────────"
	@printf "  python : "; ($(PY) -V 2>/dev/null) || echo "CHƯA CÀI"
	@printf "  docker : "; (docker -v 2>/dev/null) || echo "CHƯA CÀI  -> cần Docker Desktop"
	@printf "  compose: "; (docker compose version 2>/dev/null) || echo "CHƯA CÀI"
	@printf "  git    : "; (git --version 2>/dev/null) || echo "CHƯA CÀI"
	@printf "  make   : "; (make -v 2>/dev/null | head -1) || echo "CHƯA CÀI"
	@printf "  .env   : "; (test -f .env && echo "có" || echo "THIẾU -> cp .env.example .env")
	@printf "  venv   : "; (test -d .venv && echo "có" || echo "THIẾU -> make install")
	@$(PY) -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' \
	    && echo "  => Python OK (>=3.12)" \
	    || echo "  => CẦN Python 3.12+ (đang dùng: $$($(PY) -V 2>&1))"
	@echo "───────────────────────────────────────────────"

# ------------------------------------------------------------
# Cài đặt
# ------------------------------------------------------------
install: ## Tạo venv + cài thư viện + cài pre-commit hook
	@$(PY) -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' \
		|| { echo "❌ Cần Python 3.12+. Đang có: $$($(PY) -V 2>&1)"; \
		     echo "   macOS : brew install python@3.12"; \
		     echo "   Windows: winget install Python.Python.3.12"; exit 1; }
	@test -d .venv || $(PY) -m venv .venv
	@$(PY) -m pip install --upgrade pip -q
	@$(PY) -m pip install -r requirements.txt -r requirements-dev.txt
	@test -f .env || cp .env.example .env
	@$(PY) -m pre_commit install
	@echo ""
	@echo "✅ Cài xong. Tiếp theo: make up && make doctor"

# ------------------------------------------------------------
# Hạ tầng (Docker)
# ------------------------------------------------------------
up: ## Khởi động MySQL 8.0 (cổng 3307)
	@docker compose up -d mysql
	@echo -n "⏳ Đang chờ MySQL healthy "
	@n=0; until [ "$$(docker inspect -f '{{.State.Health.Status}}' cafetlu-mysql 2>/dev/null)" = "healthy" ]; do \
		n=$$((n+1)); [ $$n -gt 60 ] && { echo ""; echo "❌ MySQL không lên sau 60s — xem: make logs"; exit 1; }; \
		echo -n "."; sleep 1; done; echo ""
	@port=$$(grep -E '^DB_PORT=' .env 2>/dev/null | cut -d= -f2); \
		echo "✅ MySQL sẵn sàng tại 127.0.0.1:$${port:-3307} (db: cafe_tlu, user: root)"

down: ## Tắt hạ tầng
	@docker compose down

reset-db: ## XOÁ SẠCH dữ liệu MySQL rồi khởi động lại (nguy hiểm)
	@read -p "Xoá toàn bộ dữ liệu MySQL local? [y/N] " ans; \
	    [ "$$ans" = "y" ] || { echo "Đã huỷ."; exit 1; }
	@docker compose down -v
	@$(MAKE) up

logs: ## Xem log MySQL
	@docker compose logs -f mysql

tools: ## Bật Adminer (xem DB tại http://localhost:8081)
	@docker compose --profile tools up -d
	@echo "✅ Adminer: http://localhost:8081 (server: mysql, user: root, pass: xem .env)"

# ------------------------------------------------------------
# Chạy ứng dụng (sẽ dùng được sau khi có code ở tuần 1)
# ------------------------------------------------------------
api: ## Chạy backend FastAPI (cổng 8000)
	@test -f api/main.py || { echo "⏳ Chưa có api/main.py — sẽ được tạo ở tuần 1 (cổng G2)."; exit 1; }
	@$(PY) -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

gui: ## Chạy giao diện desktop
	@test -f gui/main.py || { echo "⏳ Chưa có gui/main.py — sẽ được tạo ở tuần 1 (cổng G2)."; exit 1; }
	@$(PY) -m gui.main

# ------------------------------------------------------------
# Chất lượng
# ------------------------------------------------------------
test: ## Chạy test (pytest)
	@$(PY) -m pytest -q $(PYTEST_ARGS); \
	code=$$?; \
	if [ $$code -eq 5 ]; then echo "⚠️  Chưa có test nào (giai đoạn setup) — coi như đạt."; \
	elif [ $$code -ne 0 ]; then exit $$code; fi

lint: ## Kiểm tra lint + format
	@$(PY) -m ruff check . && $(PY) -m black --check .

fmt: ## Tự sửa format + lint
	@$(PY) -m ruff check --fix . ; $(PY) -m black .

check: lint test ## Chạy lint + test (dùng trước khi mở PR)

# ------------------------------------------------------------
# Đóng gói (bật ở cổng G4)
# ------------------------------------------------------------
build-installer: ## Build bộ cài Windows (cần installer/*.iss)
	@ls installer/*.iss >/dev/null 2>&1 || { echo "⏳ Chưa có installer/*.iss — bật ở cổng G4."; exit 1; }
	@bash scripts/build_installer.sh

# ------------------------------------------------------------
# Dọn dẹp
# ------------------------------------------------------------
clean: ## Xoá cache build (không đụng dữ liệu DB)
	@find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache .ruff_cache htmlcov .coverage build dist
	@echo "✅ Đã dọn cache."
