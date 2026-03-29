from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import re

from app.core.config import settings
from app.services.yt_service import download_video
from app.api.routes.pdf import cleanup_files # Używamy naszego sprzątacza!

router = APIRouter()

# Model Pydantic do odbierania JSON-a z linkiem
class YtRequest(BaseModel):
    url: str

@router.post("/download")
def api_download_video(
    req: YtRequest,
    background_tasks: BackgroundTasks
):
    print(f"\n--- NOWE ZAPYTANIE: Pobieranie filmu z YT ---")
    print(f" -> URL: {req.url}")
    
    # Tworzymy bezpieczną ścieżkę do zapisu dla Workera
    file_id = str(uuid.uuid4())
    output_filename = f"yt_{file_id}.mp4"
    output_path = settings.DOWNLOADS_DIR / output_filename
    
    # Zlecamy zadanie do Workera Celery
    task = download_video.delay(req.url, str(output_path))
    
    print(" -> Oczekiwanie na pobranie i zmontowanie pliku przez Workera...")
    # Pobieranie może potrwać (szczególnie dużych filmów) - dajemy timeout do 5 minut (300s)
    try:
        result = task.get(timeout=300) 
    except Exception as e:
        raise HTTPException(status_code=504, detail="Przekroczono czas oczekiwania na pobranie z YT.")

    if result.get("status") == "error":
        cleanup_files([str(output_path)])
        raise HTTPException(status_code=500, detail=result.get("detail"))
        
    # Sprzątanie pobranego wideo zaraz po tym, jak wyślemy je do Angulara
    background_tasks.add_task(cleanup_files, [result["output_path"]])
    
    # Czyścimy tytuł z dziwnych znaków i emoji, żeby nie wysadziło nagłówków HTTP w przeglądarce
    raw_title = result.get("title", "wideo")
    safe_title = re.sub(r'[\\/*?:"<>|]', "", raw_title).strip()
    
    print(f" -> Odsyłanie pliku wideo ({safe_title}.mp4). Sprzątanie w tle zaplanowane.")
    
    return FileResponse(
        path=result["output_path"],
        filename=f"{safe_title}.mp4",
        media_type="video/mp4"
    )