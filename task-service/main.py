import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.task_model import Base, engine
from app.routes.task_routes import router as task_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Task Service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(task_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "task-service"}