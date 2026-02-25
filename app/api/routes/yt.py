from fastapi import APIRouter
from app.models.schemas import DownloadVideoRequest
from app.services.yt_service import download_video

router = APIRouter()

@router.post("/download")
async def api_download_video(req: DownloadVideoRequest):
    task = download_video.delay(req.url, req.output_dir)
    return {"task_id": task.id, "status": "QUEUED"}