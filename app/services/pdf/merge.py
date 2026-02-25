from app.core.celery_app import celery
import pypdf

@celery.task(bind=True, name="app.services.pdf.merge.merge_pdfs")
def merge_pdfs(self, input_paths: list[str], output_path: str):
    """
    Łączy listę plików PDF w jeden duży plik.
    :param input_paths: Lista ścieżek do plików (np. ["/tmp/1.pdf", "/tmp/2.pdf"])
    :param output_path: Ścieżka docelowa dla połączonego pliku.
    """
    self.update_state(state="PROCESSING", meta={"status": "Łączenie dokumentów PDF..."})
    
    try:
        merger = pypdf.PdfWriter()
        
        for path in input_paths:
            merger.append(path)
            
        merger.write(output_path)
        merger.close()
        
        return {"status": "done", "output_path": output_path}
    except Exception as e:
        return {"status": "error", "detail": str(e)}