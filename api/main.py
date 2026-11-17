"""Điểm vào chính của Backend FastAPI (CafeTLU).

Tuân thủ:
- WORKFLOW.md mục 4.1 & 9.3: Cấu trúc app, định dạng envelope lỗi chung.
- Issue #19 & #20: Tự sinh Swagger /docs, CORS, kiểm tra healthcheck.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.core.config import settings
from api.routers import health
from shared.error_codes import ErrorCode
from shared.errors import AppError
from shared.version import APP_NAME, __version__

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=APP_NAME,
    version=__version__,
    description="Backend API cho ứng dụng Quản lý quán café TLU",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Cấu hình CORS cho GUI và các client gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Xử lý ngoại lệ nghiệp vụ AppError theo format WORKFLOW mục 9.3."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Chuẩn hoá lỗi validate Pydantic thành VALIDATION_ERROR theo format chung."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": ErrorCode.VALIDATION_ERROR,
                "message": "Dữ liệu không hợp lệ",
                "details": {"errors": exc.errors()},
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Bắt các lỗi chưa được xử lý, không trả stack trace ra client."""
    logger.error("Lỗi hệ thống không mong muốn: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": ErrorCode.INTERNAL_SERVER_ERROR,
                "message": "Đã có lỗi xảy ra từ máy chủ",
                "details": {},
            }
        },
    )


# Mount healthcheck ở root (/health cho Dockerfile) và api/v1 (/api/v1/health theo contract)
app.include_router(health.router)
app.include_router(health.router, prefix="/api/v1")
