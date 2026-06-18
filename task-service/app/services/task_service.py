import json
import logging
from aiokafka import AIOKafkaProducer
from sqlalchemy.orm import Session

from app.repositories.task_repository import TaskRepository
from app.models.task_model import Task

logger = logging.getLogger(__name__)

VALID_STATUSES = {"pending", "in_progress", "done"}


class TaskService:
    def __init__(self, db: Session, producer: AIOKafkaProducer):
        self.repo = TaskRepository(db)
        self.producer = producer

    async def create_task(self, title: str, description: str, assigned_to: str) -> Task:
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty.")
        if not assigned_to or not assigned_to.strip():
            raise ValueError("A task must be assigned to someone.")

        task = self.repo.create(
            title=title.strip(),
            description=description,
            assigned_to=assigned_to.strip(),
        )

        await self._publish("task.created", {
            "task_id": task.id,
            "title": task.title,
            "assigned_to": task.assigned_to,
            "message": f"Task '{task.title}' was assigned to you.",
        })

        return task

    async def update_status(self, task_id: str, status: str) -> Task:
        if status not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {sorted(VALID_STATUSES)}")

        task = self.repo.update_status(task_id, status)
        if not task:
            raise LookupError(f"No task found with id '{task_id}'.")

        await self._publish("task.updated", {
            "task_id": task.id,
            "title": task.title,
            "assigned_to": task.assigned_to,
            "message": f"Task '{task.title}' status changed to '{status}'.",
        })

        return task

    def get_all_tasks(self) -> list[Task]:
        return self.repo.get_all()

    async def _publish(self, event_type: str, payload: dict):
        try:
            message = json.dumps({
                "event": event_type,
                **payload
            }).encode("utf-8")

            await self.producer.send_and_wait("task-events", message)
            logger.info(f"[Kafka] Published: {event_type} for task '{payload.get('title')}'")
        except Exception as e:
            logger.error(f"[Kafka] Failed to publish event: {e}")