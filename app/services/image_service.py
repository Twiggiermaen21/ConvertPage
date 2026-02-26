from app.core.celery_app import celery
from rembg import remove, new_session
from PIL import Image

@celery.task(bind=True, name="app.services.image_service.remove_background")
def remove_background(self, input_path: str, output_path: str):
    self.update_state(state="PROCESSING", meta={"status": "Uruchamianie zaawansowanego modelu AI..."})
    print(f"\n[WORKER] Usuwanie tła ze zdjęcia: {input_path}")
    
    try:
        input_image = Image.open(input_path)
        
        # 1. Inicjalizujemy nowszy, inteligentniejszy model do ogólnego użytku
        # (Przy pierwszym użyciu Worker pobierze ten model z internetu, co potrwa kilka sekund)
        session = new_session("isnet-general-use")
        
        # 2. Wywołujemy usuwanie tła z zaawansowanymi parametrami
        output_image = remove(
            input_image,
            session=session,              # Używamy lepszego modelu
            alpha_matting=True,           # Włączamy dokładne wygładzanie krawędzi
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10,  # Rozmiar pędzla korygującego (domyślnie 10)
            post_process_mask=True        # Dodatkowe czyszczenie artefaktów
        )
        
        output_image.save(output_path, format="PNG")
        
        input_image.close()
        output_image.close()
        
        print(f"[WORKER] Sukces! Zdjęcie bez tła zapisano w: {output_path}")
        return {"status": "done", "output_path": output_path}
        
    except Exception as e:
        print(f"[WORKER] BŁĄD PODCZAS USUWANIA TŁA: {e}")
        return {"status": "error", "detail": str(e)}