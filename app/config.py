from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


class Settings(BaseModel):
    app_name: str = os.getenv("APEX_APP_NAME", "Apex Mentor")
    db_path: Path = Path(os.getenv("APEX_DB_PATH", "data/apex_mentor.sqlite"))
    auth_token: str = os.getenv("APEX_AUTH_TOKEN", "change-this-token-before-exposing")
    host: str = os.getenv("APEX_HOST", "127.0.0.1")
    port: int = int(os.getenv("APEX_PORT", "8000"))


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
