import os
from pathlib import Path


def _load_env_file() -> None:
    env_paths = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent / ".env",
        Path(__file__).resolve().parent / ".env",
    ]

    for env_path in env_paths:
        if not env_path.exists():
            continue

        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
        break


_load_env_file()


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "")
    secret_key: str = os.getenv("SECRET_KEY", "")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_decode_responses: bool = os.getenv("REDIS_DECODE_RESPONSES", "true").lower() == "true"
    test_booking_url: str = os.getenv("TEST_BOOKING_URL", "")
    test_auth_token: str = os.getenv("TEST_AUTH_TOKEN", "")


settings = Settings()
