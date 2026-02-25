from app.core.celery_app import celery

@celery.task(bind=True, name="app.services.yt_service.download_video")
def download_video(self, url: str, output_dir: str = "./downloads"):
    import yt_dlp
    import os

    os.makedirs(output_dir, exist_ok=True)
    self.update_state(state="PROCESSING", meta={"status": "Pobieranie..."})

    ydl_opts = {
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "format": "bestaudio/best",
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
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        return {"status": "done", "filename": filename, "title": info.get("title")}
    except Exception as e:
        return {"status": "error", "detail": str(e)}