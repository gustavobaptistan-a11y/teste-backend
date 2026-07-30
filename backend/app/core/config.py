import os
import secrets
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _csv_env(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


@dataclass(frozen=True)
class Settings:
    environment: str
    database_url: str
    redis_url: str | None
    secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    cors_origins: list[str]
    sql_echo: bool


def load_settings() -> Settings:
    environment = os.getenv("ENVIRONMENT", "development").lower()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL nao configurada.")
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        if environment == "production":
            raise RuntimeError("SECRET_KEY e obrigatoria em producao.")
        secret_key = secrets.token_urlsafe(48)

    if environment == "production" and len(secret_key) < 32:
        raise RuntimeError("SECRET_KEY deve ter pelo menos 32 caracteres em producao.")

    cors_origins = _csv_env("CORS_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500")
    if environment == "production" and "*" in cors_origins:
        raise RuntimeError("CORS_ORIGINS nao pode usar '*' em producao.")

    return Settings(
        environment=environment,
        database_url=database_url,
        redis_url=os.getenv("REDIS_URL") or None,
        secret_key=secret_key,
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=_int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 30),
        cors_origins=cors_origins,
        sql_echo=_bool_env("SQL_ECHO", False),
    )


settings = load_settings()
