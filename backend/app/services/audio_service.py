from app.core.celery_app import celery
import ffmpeg

@celery.task(bind=True, name="app.services.audio_service.convert_audio")
def convert_audio(self, input_path: str, output_path: str, target_format: str):
    self.update_state(state="PROCESSING", meta={"status": f"Konwersja audio do {target_format.upper()}..."})
    print(f"\n[WORKER] Konwersja audio: {input_path} -> {output_path}")
    
    try:
        # Wczytujemy plik wejściowy (FFmpeg sam rozpozna, co to za format)
        stream = ffmpeg.input(input_path)
        
        target_format = target_format.lower()
        
        # Ustawiamy odpowiednie kodeki dla formatu wyjściowego
        if target_format == 'wav':
            stream = ffmpeg.output(stream, output_path, format='wav', acodec='pcm_s16le', ar='44100')
        elif target_format == 'mp3':
            stream = ffmpeg.output(stream, output_path, format='mp3', audio_bitrate='192k')
        elif target_format in ['m4a', 'mp4a']:
            # m4a to technicznie kontener mp4 zawierający tylko dźwięk AAC
            stream = ffmpeg.output(stream, output_path, format='ipod', acodec='aac', audio_bitrate='192k')
        else:
            stream = ffmpeg.output(stream, output_path)
            
        # Uruchamiamy FFmpeg, nadpisując plik w razie potrzeby i łapiąc logi
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        
        print(f"[WORKER] Sukces! Zapisano plik audio w: {output_path}")
        return {"status": "done", "output_path": output_path}
        
    except ffmpeg.Error as e:
        # Ten kawałek kodu jest kluczowy, bo ffmpeg-python wyrzuca błędy w bajtach (stderr)
        error_message = e.stderr.decode('utf-8') if e.stderr else str(e)
        print(f"[WORKER] BŁĄD FFMPEG: {error_message}")
        return {"status": "error", "detail": f"Błąd FFmpeg: {error_message}"}
    except Exception as e:
        print(f"[WORKER] BŁĄD SYSTEMU: {e}")
        return {"status": "error", "detail": str(e)}