# Dockerfile backend — chạy API FastAPI ở môi trường thật.
#
# Build từ gốc repo (context = repo root):
#   docker build -f infra/Dockerfile -t cafetlu-api .
# Chạy thử:
#   docker run --rm -p 8000:8000 --env-file .env cafetlu-api
#
# Lưu ý G1: file này có trước khi `api/` có code để chốt cách đóng gói.
# Khi A merge khung `api/main.py`, `docker build` mới chạy được đầy đủ.
# G4 sẽ tách requirements-api.txt để không kéo PySide6 vào image server.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# User thường, không chạy root trong container
RUN groupadd --system cafe && useradd --system --gid cafe --create-home cafe

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY api ./api
COPY shared ./shared

RUN chown -R cafe:cafe /app
USER cafe

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status == 200 else 1)"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
