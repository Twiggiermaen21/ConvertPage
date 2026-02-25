from app.core.celery_app import celery
import fitz
import zipfile
import os

@celery.task(bind=True, name="app.services.pdf.split.split_pdf")
def split_pdf(self, input_path: str, output_zip_path: str):
    """
    Rozdziela wielostronicowy PDF na pojedyncze pliki PDF i pakuje je do ZIP.
    """
    self.update_state(state="PROCESSING", meta={"status": "Rozdzielanie na pojedyncze strony..."})
    
    try:
        doc = fitz.open(input_path)
        
        # Otwieramy plik ZIP do zapisu
        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for page_num in range(len(doc)):
                # Raportujemy postęp do Angulara
                self.update_state(
                    state="PROCESSING", 
                    meta={"status": f"Wycinanie strony {page_num + 1} z {len(doc)}..."}
                )
                
                # Tworzymy nowy, pusty dokument PDF i wklejamy do niego jedną stronę
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                
                # Zapisujemy wyciętą stronę do bufora w pamięci
                pdf_bytes = new_doc.write()
                
                # Zapisujemy bajty prosto do archiwum ZIP (bez tworzenia śmieci na dysku)
                zipf.writestr(f"strona_{page_num + 1}.pdf", pdf_bytes)
                new_doc.close()
                
        doc.close()
        return {"status": "done", "output_path": output_zip_path}
    except Exception as e:
        return {"status": "error", "detail": str(e)}