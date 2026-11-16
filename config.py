"""Settings from environment variables and an optional .env file."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str
    anthropic_model: str
    db_path: Path
    words_per_second: float
    default_duration: int


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    db = Path(os.getenv("STUDIO_DB_PATH", "data/studio.db"))
    return Settings(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", "").strip(),
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5").strip(),
        db_path=db if db.is_absolute() else BASE_DIR / db,
        words_per_second=float(os.getenv("WORDS_PER_SECOND", "2.6")),
        default_duration=int(os.getenv("DEFAULT_DURATION", "45")),
    )
