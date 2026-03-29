from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import uuid
import shutil
from pathlib import Path

from app.core.config import settings
from app.services.audio_service import convert_audio
from app.api.routes.pdf import cleanup_files  # Importujemy funkcję sprzątającą!

router = APIRouter()

@router.post("/convert")
def api_convert_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_format: str = Form(...)  # Odbieramy format z Angulara np. "wav", "mp3"
):
    print(f"\n--- NOWE ZAPYTANIE: Konwersja audio z {file.filename} na {target_format} ---")

    # Sprawdzamy, czy użytkownik nie wysłał dziwnego formatu
    allowed_formats = ['wav', 'mp3', 'm4a', 'mp4a']
    target_format = target_format.lower().strip()
    
    if target_format not in allowed_formats:
        raise HTTPException(status_code=400, detail=f"Nieobsługiwany format. Wybierz: {allowed_formats}")

    file_id = str(uuid.uuid4())
    # Zapisujemy plik z jego oryginalnym rozszerzeniem (żeby FFmpeg miał łatwiej)
    original_ext = Path(file.filename).suffix
    input_path = settings.UPLOADS_DIR / f"{file_id}{original_ext}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    output_filename = f"converted_{file_id}.{target_format}"
    output_path = settings.DOWNLOADS_DIR / output_filename

    # Odpalamy Workera Celery
    task = convert_audio.delay(str(input_path), str(output_path), target_format)
    
    # Dajemy 2 minuty timeoutu dla dłuższych plików audio
    result = task.get(timeout=120) 
    
    if result.get("status") == "error":
        cleanup_files([str(input_path)])
        raise HTTPException(status_code=500, detail=result.get("detail"))
        
    # Zaplanowanie sprzątania
    files_to_delete = [str(input_path), result["output_path"]]
    background_tasks.add_task(cleanup_files, files_to_delete)
    
    print(f" -> Odsyłanie pliku {target_format.upper()}. Sprzątanie w tle zaplanowane.")
    
    original_name = Path(file.filename).stem
    return FileResponse(
        path=result["output_path"],
        filename=f"{original_name}.{target_format}",
        # Typ MIME ustawiany w zależności od wybranego rozszerzenia
        media_type=f"audio/{target_format}" if target_format not in ['m4a', 'mp4a'] else "audio/mp4"
    )