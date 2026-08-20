from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv

load_dotenv()


def parse_list(value: str) -> List[str]:
    """Parse JSON-like list string."""
    import json
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return [v.strip() for v in value.split(",") if v.strip()]


class Settings:
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://tutoring:tutoring123@localhost:3306/tutoring?charset=utf8mb4"
    )

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_days: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "7"))

    # MinIO
    minio_endpoint: str = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
    minio_bucket: str = os.getenv("MINIO_BUCKET", "tutoring-uploads")

    # CORS
    cors_origins: List[str] = parse_list(os.getenv("CORS_ORIGINS", '["http://localhost:5173"]'))

    @property
    def secret_key(self) -> str:
        return self.jwt_secret

    @property
    def algorithm(self) -> str:
        return self.jwt_algorithm


settings = Settings()
