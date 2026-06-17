from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.notification_model import get_db
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationCreate(BaseModel):
    user_id: str
    message: str
    category: str = "general"
    priority: str = "normal"


@router.post("", status_code=201)
def create_notification(body: NotificationCreate, db: Session = Depends(get_db)):
    service = NotificationService(db)
    try:
        return service.create(body.user_id, body.message, body.category, body.priority)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
def list_all(db: Session = Depends(get_db)):
    """Get every notification — useful for admin/debugging."""
    service = NotificationService(db)
    return service.get_all()


@router.get("/user/{user_id}")
def get_for_user(
    user_id: str,
    status: str = Query(None, description="unread | read"),
    category: str = Query(None, description="general | task | hr | system"),
    db: Session = Depends(get_db),
):
    service = NotificationService(db)
    return service.get_for_user(user_id, status=status, category=category)


@router.get("/user/{user_id}/unread-count")
def unread_count(user_id: str, db: Session = Depends(get_db)):
    service = NotificationService(db)
    return {"user_id": user_id, "unread": service.count_unread(user_id)}


@router.patch("/{notif_id}/read")
def mark_as_read(notif_id: str, db: Session = Depends(get_db)):
    service = NotificationService(db)
    try:
        return service.mark_read(notif_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/user/{user_id}/read-all")
def mark_all_as_read(user_id: str, db: Session = Depends(get_db)):
    service = NotificationService(db)
    return service.mark_all_read(user_id)


@router.delete("/{notif_id}", status_code=204)
def delete_notification(notif_id: str, db: Session = Depends(get_db)):
    service = NotificationService(db)
    try:
        service.delete(notif_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))