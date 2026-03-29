from app.core.celery_app import celery
import yt_dlp
import os

@celery.task(bind=True, name="app.services.yt_service.download_video")
def download_video(self, url: str, output_path: str):
    self.update_state(state="PROCESSING", meta={"status": "Rozpoczynam pobieranie..."})
    print(f"\n[WORKER] Rozpoczynam pobieranie z YT: {url}")
    
    # Konfiguracja yt-dlp dla MP4
    ydl_opts = {
        "outtmpl": output_path, # Zapisujemy od razu pod docelową ścieżką
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4", # Jeśli formaty są osobno, wymuszamy ich złączenie do mp4
        "quiet": True,
        "noplaylist": True, # Pobieramy tylko jeden film, nawet jeśli to link do playlisty
        "progress_hooks": [
            lambda d: self.update_state(
                state="PROCESSING",
                meta={"status": "Pobieranie...", "progress": d.get("_percent_str", "?")}
            )
            if d["status"] == "downloading" else None
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("[WORKER] yt-dlp analizuje link i pobiera pliki...")
            info = ydl.extract_info(url, download=True)
            video_title = info.get("title", "wideo_z_youtube")
            
        print(f"[WORKER] Sukces! Pobrane wideo: {output_path}")
        return {
            "status": "done", 
            "output_path": output_path, 
            "title": video_title
        }
    except Exception as e:
        print(f"[WORKER] BŁĄD YT-DLP: {e}")
        return {"status": "error", "detail": str(e)}