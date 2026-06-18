import json
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiokafka import AIOKafkaConsumer
from sqlalchemy.orm import Session

from app.models.notification_model import Base, engine, SessionLocal
from app.routes.notification_routes import router as notif_router
from app.services.notification_service import NotificationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP = "kafka:9092"
KAFKA_TOPIC = "task-events"


async def consume_kafka_events():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,

        auto_offset_reset="earliest",

        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    await consumer.start()
    logger.info(f"[Kafka] Consumer started. Listening on topic '{KAFKA_TOPIC}'...")

    try:
        async for message in consumer:
            event = message.value
            logger.info(f"[Kafka] Received: {event}")

            db: Session = SessionLocal()
            try:
                service = NotificationService(db)
                service.create_from_event(event)
            except Exception as e:
                logger.error(f"[Kafka] Error processing event: {e}")
            finally:
                db.close()

    finally:
        await consumer.stop()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating DB tables if they don't exist...")
    Base.metadata.create_all(bind=engine)

    logger.info("Starting Kafka consumer background task...")
    consumer_task = asyncio.create_task(consume_kafka_events())

    yield

    logger.info("Shutting down Kafka consumer...")
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Notification Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notif_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "notification-service"}