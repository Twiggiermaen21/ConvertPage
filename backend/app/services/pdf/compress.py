from app.core.celery_app import celery
import subprocess
import os
import fitz

@celery.task(bind=True, name="app.services.pdf.compress.compress_pdf")
def compress_pdf(self, input_path: str, output_path: str, dpi: str = "150"):
    self.update_state(state="PROCESSING", meta={"status": f"Kompresja pliku (DPI: {dpi})..."})
    print(f"\n[WORKER] Kompresowanie pliku: {input_path} z docelowym DPI: {dpi}")
    
    try:
        dpi_value = int(dpi)
    except ValueError:
        dpi_value = 150

    if dpi_value <= 72:
        gs_setting = "/screen"
    elif dpi_value <= 150:
        gs_setting = "/ebook"
    elif dpi_value <= 300:
        gs_setting = "/printer"
    else:
        gs_setting = "/prepress"

    gs_command = "gswin64c" if os.name == 'nt' else "gs"
    command = [
        gs_command, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={gs_setting}", "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_path}", input_path
    ]
    
    # Flaga, która powie nam, czy kompresja Ghostscript się udała
    ghostscript_success = False

    try:
        print(f"[WORKER] Uruchamianie kompresji z presetem {gs_setting}...")
        process = subprocess.run(command, capture_output=True, text=True)
        
        if process.returncode == 0 and os.path.exists(output_path):
            ghostscript_success = True
        else:
            print(f"[WORKER] Błąd Ghostscript: {process.stderr}")
            
    except FileNotFoundError:
        print(f"[WORKER] UWAGA: Nie znaleziono programu Ghostscript ({gs_command}) na tym komputerze.")
    except Exception as e:
        print(f"[WORKER] Inny błąd wywołania Ghostscript: {e}")

    # Jeśli Ghostscript zawiódł (lub w ogóle go nie masz), używamy koła ratunkowego
    if not ghostscript_success:
        print("[WORKER] Próba zapasowej kompresji przez PyMuPDF...")
        try:
            doc = fitz.open(input_path)
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
        except Exception as e:
            return {"status": "error", "detail": f"Błąd kompresji awaryjnej: {e}"}
            
    print(f"[WORKER] Sukces! Plik skompresowany i zapisany w: {output_path}")
    return {"status": "done", "output_path": output_path}