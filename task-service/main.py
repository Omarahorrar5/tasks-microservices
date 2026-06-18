import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiokafka import AIOKafkaProducer

from app.models.task_model import Base, engine
from app.routes.task_routes import router as task_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP = "kafka:9092"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating DB tables if they don't exist...")
    Base.metadata.create_all(bind=engine)

    logger.info("Starting Kafka producer...")
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP)
    await producer.start()

    app.state.producer = producer
    logger.info("Kafka producer ready.")

    yield

    logger.info("Stopping Kafka producer...")
    await producer.stop()


app = FastAPI(
    title="Task Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "task-service"}