from app.core.celery_app import celery
import fitz  # Używamy PyMuPDF zamiast pypdf

@celery.task(bind=True, name="app.services.pdf.merge.merge_pdfs")
def merge_pdfs(self, input_paths: list[str], output_path: str):
    """
    Łączy listę plików PDF w jeden duży plik za pomocą niezawodnego PyMuPDF.
    """
    self.update_state(state="PROCESSING", meta={"status": "Łączenie dokumentów PDF..."})
    print(f"\n[WORKER] Łączenie plików: {input_paths} \n -> Do: {output_path}")
    
    try:
        # 1. Tworzymy nowy, pusty dokument wynikowy
        result_pdf = fitz.open()
        
        # 2. Przechodzimy przez wszystkie ścieżki
        for path in input_paths:
            # Otwieramy plik bezpiecznie w kontekście 'with'
            with fitz.open(path) as current_pdf:
                # Wklejamy całą zawartość aktualnego pliku do pliku wynikowego
                result_pdf.insert_pdf(current_pdf)
                
        # 3. Zapisujemy połączony plik fizycznie na dysku
        result_pdf.save(output_path)
        result_pdf.close()
        
        print(f"[WORKER] Sukces! Plik zapisany w: {output_path}")
        return {"status": "done", "output_path": output_path}
        
    except Exception as e:
        print(f"[WORKER] BŁĄD PODCZAS ŁĄCZENIA: {e}")
        return {"status": "error", "detail": str(e)}