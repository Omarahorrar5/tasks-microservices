from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.task_model import get_db
from app.services.task_service import TaskService
from app.repositories.task_repository import TaskRepository

router = APIRouter(prefix="/tasks", tags=["Tasks"])


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    assigned_to: str


class StatusUpdate(BaseModel):
    status: str


@router.post("", status_code=201)
async def create_task(body: TaskCreate, request: Request, db: Session = Depends(get_db)):
    service = TaskService(db, request.app.state.producer)
    try:
        return await service.create_task(body.title, body.description, body.assigned_to)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
def list_tasks(db: Session = Depends(get_db)):
    repo = TaskRepository(db)
    return repo.get_all()


@router.patch("/{task_id}/status")
async def update_task_status(task_id: str, body: StatusUpdate, request: Request, db: Session = Depends(get_db)):
    service = TaskService(db, request.app.state.producer)
    try:
        return await service.update_status(task_id, body.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))