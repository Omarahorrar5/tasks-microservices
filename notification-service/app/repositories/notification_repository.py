from sqlalchemy.orm import Session
from app.models.notification_model import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str, message: str, category: str,
               priority: str, source_event: str = None) -> Notification:
        notif = Notification(
            user_id=user_id,
            message=message,
            category=category,
            priority=priority,
            source_event=source_event,
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def get_all(self) -> list[Notification]:
        return self.db.query(Notification).order_by(Notification.created_at.desc()).all()

    def get_by_user(self, user_id: str, status: str = None, category: str = None) -> list[Notification]:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)

        if status == "unread":
            query = query.filter(Notification.is_read == False)
        elif status == "read":
            query = query.filter(Notification.is_read == True)

        if category:
            query = query.filter(Notification.category == category)

        return query.order_by(Notification.created_at.desc()).all()

    def get_by_id(self, notif_id: str) -> Notification | None:
        return self.db.query(Notification).filter(Notification.id == notif_id).first()

    def mark_as_read(self, notif_id: str) -> Notification | None:
        notif = self.get_by_id(notif_id)
        if notif:
            notif.is_read = True
            self.db.commit()
            self.db.refresh(notif)
        return notif

    def mark_all_read(self, user_id: str) -> int:
        unread = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .all()
        )
        for notif in unread:
            notif.is_read = True
        self.db.commit()
        return len(unread)

    def delete(self, notif_id: str) -> bool:
        notif = self.get_by_id(notif_id)
        if notif:
            self.db.delete(notif)
            self.db.commit()
            return True
        return False

    def count_unread(self, user_id: str) -> int:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .count()
        )