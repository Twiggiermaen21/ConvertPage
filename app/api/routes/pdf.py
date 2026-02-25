from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import uuid
import shutil
from pathlib import Path

from app.core.config import settings
from app.services.pdf.merge import merge_pdfs

router = APIRouter()

@router.post("/merge")
async def api_merge_pdfs(files: List[UploadFile] = File(...)):
    # 1. Wyświetlamy w konsoli FastAPI informację o nowym żądaniu
    print(f"\n--- NOWE ZAPYTANIE Z ANGULARA: Łączenie {len(files)} plików ---")

    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Wymagane są co najmniej 2 pliki do połączenia.")

    input_paths = []
    
    # 2. Przechodzimy przez każdy przesłany plik
    for file in files:
        # Wyświetlamy oryginalną nazwę pliku, która przyszła z frontendu
        print(f" -> Odbieranie pliku: {file.filename} (Typ: {file.content_type})")
        
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}_{file.filename}"
        
        # Tworzymy pełną ścieżkę do zapisu w folderze uploads
        file_path = settings.UPLOADS_DIR / safe_filename
        
        # 3. ZAPISUJEMY plik PDF na dysku serwera
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f" -> Pomyślnie zapisano plik na dysku: {file_path}")
        input_paths.append(str(file_path))

    # Przygotowujemy ścieżkę dla gotowego pliku wynikowego
    output_filename = f"merged_{uuid.uuid4()}.pdf"
    output_path = settings.DOWNLOADS_DIR / output_filename

    print(f" -> Zlecanie zadania do Celery. Wynik ląduje w: {output_path}")

    # 4. Odpalamy Twoje zadanie Celery, podając mu tylko ścieżki do zapisanych plików
    task = merge_pdfs.delay(input_paths, str(output_path))
    return {"task_id": task.id, "status": "QUEUED"}