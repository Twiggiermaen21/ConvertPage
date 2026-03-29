from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
import uuid
import shutil
import json
import os
from pathlib import Path

from app.core.config import settings
from app.services.pdf.merge import merge_pdfs
from app.services.pdf.split import split_pdf
from app.services.pdf.compress import compress_pdf
from app.services.pdf.to_jpg import convert_to_jpg

router = APIRouter()

# --- FUNKCJA SPRZĄTAJĄCA ---
def cleanup_files(paths: List[str]):
    """Usuwa pliki z dysku, ignorując błędy, jeśli plik już nie istnieje."""
    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"[CLEANUP] Usunięto plik: {path}")
        except Exception as e:
            print(f"[CLEANUP] Błąd przy usuwaniu {path}: {e}")

@router.post("/to-jpg")
def api_pdf_to_jpg(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    dpi: str = Form("300")  # Pozwalamy Angularowi przysłać własne DPI, domyślnie "300"
):
    print(f"\n--- NOWE ZAPYTANIE: Konwersja do JPG pliku {file.filename} (DPI: {dpi}) ---")

    file_id = str(uuid.uuid4())
    input_path = settings.UPLOADS_DIR / f"{file_id}_{file.filename}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Zapisujemy jako archiwum ZIP, bo stron może być wiele
    output_filename = f"images_{file_id}.zip"
    output_path = settings.DOWNLOADS_DIR / output_filename

    # Zlecamy zadanie Workerowi
    task = convert_to_jpg.delay(str(input_path), str(output_path), dpi)
    
    # Wyższe DPI wymaga więcej czasu, więc dajemy 120 sekund timeoutu
    result = task.get(timeout=120) 
    
    if result.get("status") == "error":
        cleanup_files([str(input_path)])
        raise HTTPException(status_code=500, detail=result.get("detail"))
        
    # Standardowe sprzątanie
    files_to_delete = [str(input_path), result["output_path"]]
    background_tasks.add_task(cleanup_files, files_to_delete)
    
    print(" -> Odsyłanie paczki ZIP ze zdjęciami. Sprzątanie zaplanowane w tle.")
    
    original_name = Path(file.filename).stem
    return FileResponse(
        path=result["output_path"],
        filename=f"{original_name}_JPG.zip",
        media_type="application/zip"
    )

# --- ENDPOINT: MERGE ---
@router.post("/merge")
def api_merge_pdfs(
    background_tasks: BackgroundTasks, # 1. Wstrzykujemy BackgroundTasks
    files: List[UploadFile] = File(...)
):
    print(f"\n--- NOWE ZAPYTANIE: Łączenie {len(files)} plików ---")

    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Wymagane są co najmniej 2 pliki.")

    input_paths = []
    
    for file in files:
        file_id = str(uuid.uuid4())
        file_path = settings.UPLOADS_DIR / f"{file_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        input_paths.append(str(file_path))

    output_filename = f"merged_{uuid.uuid4()}.pdf"
    output_path = settings.DOWNLOADS_DIR / output_filename

    task = merge_pdfs.delay(input_paths, str(output_path))
    result = task.get(timeout=60)
    
    if result.get("status") == "error":
        # W razie błędu sprzątamy od razu przesłane pliki
        cleanup_files(input_paths)
        raise HTTPException(status_code=500, detail=result.get("detail"))
        
    # 2. Zlecamy usunięcie wszystkich plików wejściowych ORAZ pliku wyjściowego po wysłaniu!
    files_to_delete = input_paths + [result["output_path"]]
    background_tasks.add_task(cleanup_files, files_to_delete)
    
    print(" -> Odsyłanie pliku. Sprzątanie zaplanowane w tle.")
    return FileResponse(
        path=result["output_path"],
        filename=output_filename,
        media_type="application/pdf"
    )

# --- ENDPOINT: SPLIT ---
@router.post("/split")
def api_split_pdf(
    background_tasks: BackgroundTasks, # 1. Wstrzykujemy BackgroundTasks
    file: UploadFile = File(...),
    split_config: str = Form(...)
):
    print(f"\n--- NOWE ZAPYTANIE: Rozdzielanie pliku {file.filename} ---")
    
    try:
        config_data = json.loads(split_config)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Nieprawidłowy format JSON.")

    file_id = str(uuid.uuid4())
    input_path = settings.UPLOADS_DIR / f"{file_id}_{file.filename}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    output_filename = f"split_{file_id}.zip"
    output_path = settings.DOWNLOADS_DIR / output_filename

    task = split_pdf.delay(str(input_path), str(output_path), config_data)
    result = task.get(timeout=60)
    
    if result.get("status") == "error":
        # W razie błędu sprzątamy od razu
        cleanup_files([str(input_path)])
        raise HTTPException(status_code=500, detail=result.get("detail"))
        
    # 2. Zlecamy usunięcie pliku źródłowego ORAZ gotowego ZIP-a po wysłaniu
    files_to_delete = [str(input_path), result["output_path"]]
    background_tasks.add_task(cleanup_files, files_to_delete)
    
    print(" -> Odsyłanie paczki ZIP. Sprzątanie zaplanowane w tle.")
    return FileResponse(
        path=result["output_path"],
        filename=output_filename,
        media_type="application/zip"
    )

# --- ENDPOINT: COMPRESS ---
@router.post("/compress")
def api_compress_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    dpi: str = Form("150")  # <-- Odbieramy docelowe DPI (domyślnie 150, jeśli Angular nic nie wyśle)
):
    print(f"\n--- NOWE ZAPYTANIE: Kompresja pliku {file.filename} (DPI: {dpi}) ---")

    file_id = str(uuid.uuid4())
    input_path = settings.UPLOADS_DIR / f"{file_id}_{file.filename}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    output_filename = f"compressed_{file_id}.pdf"
    output_path = settings.DOWNLOADS_DIR / output_filename

    # Zlecamy zadanie do Celery przekazując wartość DPI
    task = compress_pdf.delay(str(input_path), str(output_path), dpi)
    
    result = task.get(timeout=120)
    
    if result.get("status") == "error":
        cleanup_files([str(input_path)])
        raise HTTPException(status_code=500, detail=result.get("detail"))
        
    files_to_delete = [str(input_path), result["output_path"]]
    background_tasks.add_task(cleanup_files, files_to_delete)
    
    print(" -> Odsyłanie skompresowanego pliku. Sprzątanie zaplanowane w tle.")
    
    return FileResponse(
        path=result["output_path"],
        filename=f"skompresowany_{file.filename}",
        media_type="application/pdf"
    )