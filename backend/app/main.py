from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.celery_app import celery as celery_app_instance
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Podłączamy wszystkie endpointy z naszego huba
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Backend działa 🚀"}

# Zostawiamy Twój sprawdzacz statusu zadań
@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    result = celery_app_instance.AsyncResult(task_id)
    response = {"task_id": task_id, "status": result.state}

    if result.state == "PROCESSING":
        response["meta"] = result.info
    elif result.state == "SUCCESS":
        response["result"] = result.result
    elif result.state == "FAILURE":
        response["error"] = str(result.result)

    return response