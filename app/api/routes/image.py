from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import uuid
import shutil
from pathlib import Path

from app.core.config import settings
from app.services.image_service import remove_background
from app.api.routes.pdf import cleanup_files  # Używamy naszego sprzątacza!

router = APIRouter()

@router.post("/remove-background")
def api_remove_background(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    print(f"\n--- NOWE ZAPYTANIE: Usuwanie tła z {file.filename} ---")

    file_id = str(uuid.uuid4())
    # Zapisujemy plik tymczasowo z jego oryginalnym rozszerzeniem
    original_ext = Path(file.filename).suffix
    input_path = settings.UPLOADS_DIR / f"{file_id}{original_ext}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Ustawiamy rozszerzenie PNG dla pliku wyjściowego
    output_filename = f"no_bg_{file_id}.png"
    output_path = settings.DOWNLOADS_DIR / output_filename

    # Odpalamy Workera Celery
    task = remove_background.delay(str(input_path), str(output_path))
    
    # Usuwanie tła to ciężka praca. Dajemy Workerowi 2 minuty timeoutu
    result = task.get(timeout=120) 
    
    if result.get("status") == "error":
        cleanup_files([str(input_path)])
        raise HTTPException(status_code=500, detail=result.get("detail"))
        
    # Standardowe sprzątanie
    files_to_delete = [str(input_path), result["output_path"]]
    background_tasks.add_task(cleanup_files, files_to_delete)
    
    print(" -> Odsyłanie zdjęcia bez tła. Sprzątanie w tle zaplanowane.")
    
    original_name = Path(file.filename).stem
    return FileResponse(
        path=result["output_path"],
        filename=f"{original_name}_przezroczysty.png",
        media_type="image/png"  # Koniecznie image/png!
    )