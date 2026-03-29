from pydantic_settings import BaseSettings
from pathlib import Path
import os

# Złapanie głównego katalogu projektu (dwa foldery wyżej niż config.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # Podstawowe informacje
    APP_NAME: str = "Konwerter API"
    VERSION: str = "0.2.0"
    
    # Konfiguracja Redis (Celery)
    REDIS_BROKER_URL: str = "redis://localhost:6379/0"
    REDIS_BACKEND_URL: str = "redis://localhost:6379/1"
    
    # Ścieżki robocze dla plików
    TEMP_WORKSPACE: Path = BASE_DIR / "temp_workspace"
    DOWNLOADS_DIR: Path = TEMP_WORKSPACE / "downloads"
    UPLOADS_DIR: Path = TEMP_WORKSPACE / "uploads"
    
    class Config:
        # FastAPI będzie automatycznie szukać pliku .env i nadpisywać te zmienne
        env_file = ".env"

# Tworzymy instancję ustawień, którą będziemy importować w innych plikach
settings = Settings()

# Automatyczne tworzenie folderów roboczych przy starcie aplikacji, jeśli nie istnieją
os.makedirs(settings.DOWNLOADS_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)