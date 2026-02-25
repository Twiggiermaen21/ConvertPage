from app.core.celery_app import celery
import subprocess
import os

@celery.task(bind=True, name="app.services.pdf.compress.compress_pdf")
def compress_pdf(self, input_path: str, output_path: str):
    """
    Kompresuje plik PDF przy użyciu Ghostscript (drastyczne zmniejszenie wagi obrazów).
    """
    self.update_state(state="PROCESSING", meta={"status": "Głęboka optymalizacja rozmiaru pliku..."})
    
    # Wykrywanie systemu (gswin64c dla Windows, gs dla Linux/Docker)
    gs_command = "gswin64c" if os.name == 'nt' else "gs"
    
    # Komenda dla Ghostscript ustawiająca jakość na "ebook" (ok. 150 DPI)
    command = [
        gs_command,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook", # Opcje: /screen (72 dpi), /ebook (150 dpi), /printer (300 dpi)
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ]
    
    try:
        # Uruchamiamy komendę w systemie
        process = subprocess.run(command, capture_output=True, text=True)
        
        if process.returncode != 0:
            raise Exception(f"Błąd Ghostscript: {process.stderr}")
            
        return {"status": "done", "output_path": output_path}
    except Exception as e:
        return {"status": "error", "detail": str(e)}