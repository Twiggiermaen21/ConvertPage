from app.core.celery_app import celery
import fitz
import zipfile
import os

@celery.task(bind=True, name="app.services.pdf.to_jpg.convert_to_jpg")
def convert_to_jpg(self, input_path: str, output_zip_path: str, dpi: str = "300"):
    self.update_state(state="PROCESSING", meta={"status": f"Konwersja na JPG (DPI: {dpi})..."})
    print(f"\n[WORKER] Konwersja pliku PDF do JPG: {input_path} z DPI: {dpi}")
    
    try:
        dpi_value = int(dpi)
    except ValueError:
        dpi_value = 300

    try:
        doc = fitz.open(input_path)
        
        # Obliczamy współczynnik powiększenia. 
        # PyMuPDF domyślnie renderuje w 72 DPI, więc dzielimy docelowe DPI przez 72.
        zoom = dpi_value / 72.0
        mat = fitz.Matrix(zoom, zoom)
        
        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for page_num in range(len(doc)):
                self.update_state(
                    state="PROCESSING", 
                    meta={"status": f"Renderowanie strony {page_num + 1} z {len(doc)}..."}
                )
                print(f"[WORKER] Renderowanie strony {page_num + 1}...")
                
                page = doc.load_page(page_num)
                
                # Renderujemy stronę do "pixmapy" (surowego obrazu w pamięci) z użyciem naszej matrycy jakości
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Zapisujemy wygenerowany obraz w pamięci jako bajty formatu JPG
                img_bytes = pix.tobytes("jpg")
                
                # Wrzucamy obraz prosto do pliku ZIP, używając w miarę bezpiecznej nazwy
                filename = f"strona_{page_num + 1}.jpg"
                zipf.writestr(filename, img_bytes)
                
        doc.close()
        
        print(f"[WORKER] Sukces! Zapisano archiwum ZIP ze zdjęciami w: {output_zip_path}")
        return {"status": "done", "output_path": output_zip_path}
        
    except Exception as e:
        print(f"[WORKER] BŁĄD PODCZAS KONWERSJI DO JPG: {e}")
        return {"status": "error", "detail": str(e)}