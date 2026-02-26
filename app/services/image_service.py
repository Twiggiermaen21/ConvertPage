from app.core.celery_app import celery
from rembg import remove
from PIL import Image
import os

@celery.task(bind=True, name="app.services.image_service.remove_background")
def remove_background(self, input_path: str, output_path: str):
    self.update_state(state="PROCESSING", meta={"status": "Uruchamianie modelu AI i usuwanie tła..."})
    print(f"\n[WORKER] Usuwanie tła ze zdjęcia: {input_path}")
    
    try:
        # Otwieramy plik wejściowy (biblioteka PIL)
        input_image = Image.open(input_path)
        
        # --- WIELKA MAGIA AI ---
        # Wywołujemy funkcję rembg.remove, która analizuje zdjęcie i zwraca obraz bez tła
        output_image = remove(input_image)
        
        # Zapisujemy wynik fizycznie na dysku w formacie PNG
        output_image.save(output_path, format="PNG")
        
        # Zamykamy pliki, żeby zwolnić zasoby
        input_image.close()
        output_image.close()
        
        print(f"[WORKER] Sukces! Zdjęcie bez tła zapisano w: {output_path}")
        return {"status": "done", "output_path": output_path}
        
    except Exception as e:
        print(f"[WORKER] BŁĄD PODCZAS USUWANIA TŁA: {e}")
        return {"status": "error", "detail": str(e)}