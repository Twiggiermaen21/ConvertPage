from app.core.celery_app import celery
import fitz
import zipfile
import re

@celery.task(bind=True, name="app.services.pdf.split.split_pdf")
def split_pdf(self, input_path: str, output_zip_path: str, split_config: list):
    self.update_state(state="PROCESSING", meta={"status": "Rozdzielanie dokumentu..."})
    print(f"\n[WORKER] Rozdzielanie pliku: {input_path}")
    print(f"[WORKER] Otrzymano {len(split_config)} aren/grup do wycięcia.")
    
    try:
        doc = fitz.open(input_path)
        
        # Otwieramy plik ZIP do zapisu
        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            
            # Przechodzimy przez każdą "arenę" (grupę) z Twojego Angulara
            for idx, arena in enumerate(split_config):
                label = arena.get("label", f"dokument_{idx+1}")
                pages = arena.get("pages", [])
                
                if not pages:
                    continue
                    
                # Bezpieczna nazwa pliku (usuwamy dziwne znaki, które mogłyby zepsuć system plików)
                safe_label = re.sub(r'[\\/*?:"<>|]', "", label).strip()
                if not safe_label:
                    safe_label = f"dokument_{idx+1}"
                    
                print(f"[WORKER] Tworzenie: {safe_label}.pdf (strony: {pages})")
                
                # Tworzymy nowy, czysty dokument PDF dla tej grupy
                new_doc = fitz.open()
                
                # Wklejamy wskazane strony
                for page_num in pages:
                    # Zamieniamy na indeksowanie od 0 (zakładam, że Angular wysyła 1, 2, 3...)
                    actual_page = int(page_num) - 1 
                    
                    # Zabezpieczenie przed próbą wycięcia strony, która nie istnieje
                    if 0 <= actual_page < len(doc):
                        new_doc.insert_pdf(doc, from_page=actual_page, to_page=actual_page)
                
                # Zapisujemy nowo utworzony PDF bezpośrednio do archiwum ZIP (w pamięci RAM)
                pdf_bytes = new_doc.write()
                zipf.writestr(f"{safe_label}.pdf", pdf_bytes)
                
                new_doc.close()
                
        doc.close()
        print(f"[WORKER] Sukces! Zapisano archiwum w: {output_zip_path}")
        return {"status": "done", "output_path": output_zip_path}
        
    except Exception as e:
        print(f"[WORKER] BŁĄD PODCZAS ROZDZIELANIA: {e}")
        return {"status": "error", "detail": str(e)}