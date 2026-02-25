from fastapi import APIRouter
from app.api.routes import yt
# from app.api.routes import audio, pdf  <-- Odkomentujesz, gdy utworzysz te pliki

api_router = APIRouter()

api_router.include_router(yt.router, prefix="/yt", tags=["YouTube"])
# api_router.include_router(audio.router, prefix="/audio", tags=["Audio"])
# api_router.include_router(pdf.router, prefix="/pdf", tags=["PDF"])