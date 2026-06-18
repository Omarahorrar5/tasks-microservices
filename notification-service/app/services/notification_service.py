import logging
from sqlalchemy.orm import Session
from app.repositories.notification_repository import NotificationRepository
from app.models.notification_model import Notification

logger = logging.getLogger(__name__)

VALID_PRIORITIES = {"low", "normal", "high"}
VALID_CATEGORIES = {"general", "task", "hr", "system"}


class NotificationService:
    def __init__(self, db: Session):
        self.repo = NotificationRepository(db)

    def create(self, user_id: str, message: str,
               category: str = "general", priority: str = "normal",
               source_event: str = None) -> Notification:
        if not message or not message.strip():
            raise ValueError("Message cannot be empty.")
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty.")
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of: {sorted(VALID_PRIORITIES)}")
        if category not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of: {sorted(VALID_CATEGORIES)}")

        return self.repo.create(
            user_id=user_id.strip(),
            message=message.strip(),
            category=category,
            priority=priority,
            source_event=source_event,
        )

    def get_all(self) -> list[Notification]:
        return self.repo.get_all()

    def get_for_user(self, user_id: str, status: str = None, category: str = None):
        return self.repo.get_by_user(user_id, status=status, category=category)

    def mark_read(self, notif_id: str) -> Notification:
        notif = self.repo.mark_as_read(notif_id)
        if not notif:
            raise LookupError(f"Notification '{notif_id}' not found.")
        return notif

    def mark_all_read(self, user_id: str) -> dict:
        count = self.repo.mark_all_read(user_id)
        return {"marked_read": count}

    def delete(self, notif_id: str):
        deleted = self.repo.delete(notif_id)
        if not deleted:
            raise LookupError(f"Notification '{notif_id}' not found.")

    def count_unread(self, user_id: str) -> int:
        return self.repo.count_unread(user_id)

    def create_from_event(self, event: dict):
        event_type = event.get("event", "unknown")
        user_id = event.get("assigned_to")
        message = event.get("message")

        if not user_id or not message:
            logger.warning(f"[Kafka] Skipping malformed event: {event}")
            return

        priority = "high" if event_type == "task.created" else "normal"

        logger.info(f"[Kafka] Creating notification for '{user_id}': {message}")

        return self.create(
            user_id=user_id,
            message=message,
            category="task",
            priority=priority,
            source_event=event_type,
        )