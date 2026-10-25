"""Environment-driven security settings; secrets never belong in source control."""
from dataclasses import dataclass
import os
from pathlib import Path


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes"}


@dataclass(frozen=True)
class Settings:
    environment: str = os.getenv("APP_ENV", "development")
    database_path: Path = Path(os.getenv("AUTH_DATABASE_PATH", "data/runtime/auth.sqlite3"))
    cookie_name: str = os.getenv("SESSION_COOKIE_NAME", "ldrp_session")
    session_idle_seconds: int = int(os.getenv("SESSION_IDLE_SECONDS", "1800"))
    session_absolute_seconds: int = int(os.getenv("SESSION_ABSOLUTE_SECONDS", "28800"))
    login_limit: int = int(os.getenv("LOGIN_RATE_LIMIT", "5"))
    login_window_seconds: int = int(os.getenv("LOGIN_RATE_WINDOW_SECONDS", "900"))
    frontend_origins: tuple[str, ...] = tuple(x.strip() for x in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if x.strip())

    @property
    def secure_cookies(self) -> bool:
        return _bool("SESSION_COOKIE_SECURE", self.environment == "production")


settings = Settings()
