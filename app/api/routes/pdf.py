from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import uuid
import shutil
from pathlib import Path

from app.core.config import settings
from app.services.pdf.merge import merge_pdfs
from app.services.pdf.split import split_pdf
from app.services.pdf.compress import compress_pdf

router = APIRouter()

@router.post("/merge")
async def api_merge_pdfs(files: List[UploadFile] = File(...)):
    """Przyjmuje wiele plików PDF i zleca ich połączenie."""
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Wymagane są co najmniej 2 pliki do połączenia.")

    input_paths = []
    
    # Zapisujemy każdy przesłany plik na dysku serwera
    for file in files:
        file_id = str(uuid.uuid4())
        # Bezpieczna nazwa pliku: unikalne ID + oryginalna nazwa
        safe_filename = f"{file_id}_{file.filename}"
        file_path = settings.UPLOADS_DIR / safe_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        input_paths.append(str(file_path))

    # Przygotowujemy ścieżkę dla gotowego pliku wynikowego
    output_filename = f"merged_{uuid.uuid4()}.pdf"
    output_path = settings.DOWNLOADS_DIR / output_filename

    # Wrzucamy zadanie do Redisa/Celery i natychmiast zwracamy odpowiedź do Angulara
    task = merge_pdfs.delay(input_paths, str(output_path))
    return {"task_id": task.id, "status": "QUEUED"}


@router.post("/split")
async def api_split_pdf(file: UploadFile = File(...)):
    """Przyjmuje jeden plik PDF i zleca jego rozdzielenie do archiwum ZIP."""
    file_id = str(uuid.uuid4())
    input_path = settings.UPLOADS_DIR / f"{file_id}_{file.filename}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    output_filename = f"split_{file_id}.zip"
    output_path = settings.DOWNLOADS_DIR / output_filename

    task = split_pdf.delay(str(input_path), str(output_path))
    return {"task_id": task.id, "status": "QUEUED"}


@router.post("/compress")
async def api_compress_pdf(file: UploadFile = File(...)):
    """Przyjmuje jeden plik PDF i zleca jego kompresję."""
    file_id = str(uuid.uuid4())
    input_path = settings.UPLOADS_DIR / f"{file_id}_{file.filename}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    output_filename = f"compressed_{file_id}.pdf"
    output_path = settings.DOWNLOADS_DIR / output_filename

    task = compress_pdf.delay(str(input_path), str(output_path))
    return {"task_id": task.id, "status": "QUEUED"}