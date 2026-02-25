from app.core.celery_app import celery
import fitz

@celery.task(bind=True, name="app.services.pdf.compress.compress_pdf")
def compress_pdf(self, input_path: str, output_path: str):
    """
    Kompresuje plik PDF poprzez usunięcie zduplikowanych elementów
    oraz kompresję strumieni danych (deflate).
    """
    self.update_state(state="PROCESSING", meta={"status": "Optymalizacja rozmiaru pliku..."})
    
    try:
        doc = fitz.open(input_path)
        
        # garbage=4: Usuwa wszystko, co nieużywane i duplikaty.
        # deflate=True: Kompresuje strumienie danych.
        # clean=True: Czyści strumienie z błędów składniowych.
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()
        
        return {"status": "done", "output_path": output_path}
    except Exception as e:
        return {"status": "error", "detail": str(e)}