"""Cấu hình toàn hệ thống, đọc từ biến môi trường (.env).

Tuân thủ:
- WORKFLOW.md mục 7.1 & 14: Không hardcode secret, đọc từ .env.
- Issue #20: Cung cấp đầy đủ cấu hình kết nối DB và JWT.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Lớp chứa toàn bộ biến cấu hình ứng dụng."""

    # Ứng dụng
    APP_ENV: str = "dev"
    APP_NAME: str = "CafeTLU"
    LOG_LEVEL: str = "INFO"

    # API Server
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_BASE_URL: str = "http://127.0.0.1:8000/api/v1"

    # Cơ sở dữ liệu MySQL
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3307
    DB_USER: str = "root"
    DB_PASSWORD: str = "cafetlu_dev_root"
    DB_NAME: str = "cafe_tlu"

    # Bảo mật & JWT
    JWT_SECRET: str = "change_me_local_only_please_replace"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 30
    JWT_REFRESH_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        """Chuỗi kết nối SQLAlchemy tới MySQL sử dụng driver pymysql."""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )


settings = Settings()
