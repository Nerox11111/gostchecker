from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    vk_secret_key: str = os.getenv("VK_SECRET_KEY", "")
    vk_app_id: int = int(os.getenv("VK_APP_ID", "0"))
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))
    db_path: Path = Path(os.getenv("DB_PATH", "./data/db.sqlite3"))
    model_path: Path = Path(os.getenv("MODEL_PATH", "./data/models/classifier.joblib"))
    files_ttl_days: int = int(os.getenv("FILES_TTL_DAYS", "7"))
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")

    @property
    def files_dir(self) -> Path:
        return self.data_dir / "files"

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


settings = Settings()


def get_cors_origins() -> list[str]:
    raw = settings.cors_origins.strip()
    if raw == "*":
        return ["*"]
    return [item.strip() for item in raw.split(",") if item.strip()]


def ensure_data_dirs() -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.files_dir.mkdir(parents=True, exist_ok=True)
    settings.model_path.parent.mkdir(parents=True, exist_ok=True)
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
