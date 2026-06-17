from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.task_model import get_db
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    assigned_to: str


class StatusUpdate(BaseModel):
    status: str


@router.post("", status_code=201)
def create_task(body: TaskCreate, db: Session = Depends(get_db)):
    service = TaskService(db)
    try:
        task = service.create_task(body.title, body.description, body.assigned_to)
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
def list_tasks(db: Session = Depends(get_db)):
    service = TaskService(db)
    return service.get_all_tasks()


@router.patch("/{task_id}/status")
def update_task_status(task_id: str, body: StatusUpdate, db: Session = Depends(get_db)):
    service = TaskService(db)
    try:
        task = service.update_status(task_id, body.status)
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))