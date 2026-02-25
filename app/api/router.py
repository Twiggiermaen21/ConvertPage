from fastapi import APIRouter
from app.api.routes import yt
from app.api.routes import pdf  # <-- Dodajemy import naszego nowego pliku

api_router = APIRouter()

api_router.include_router(yt.router, prefix="/yt", tags=["YouTube"])
api_router.include_router(pdf.router, prefix="/pdf", tags=["PDF"]) # <-- Rejestrujemy ścieżki PDF